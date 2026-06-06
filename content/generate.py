"""
B2/B3 — Training spec generator (Person B).

Public API (do not change signature without team sync):
    generate_spec(meta: dict) -> dict

Raises GenerateError on unrecoverable failure.

Pipeline (two-stage):
  Stage 1 — outline_call: meta -> slide plan (titles, blocks, time budget)
  Stage 2 — content_call: outline -> full spec JSON with bullets, tables, notes
"""
import json
import os
import re
from pathlib import Path

from openai import OpenAI
import jsonschema
from dotenv import load_dotenv

load_dotenv()

SCHEMA  = json.loads(Path("schema/training_spec.schema.json").read_text())
LAYOUTS = json.loads(Path("schema/layouts.json").read_text())

# Target ~1 slide per 6 minutes — ~15 slides for 90 min, ~20 for 2 hrs, ~24 for 3 hrs.
# Capped at 24 so the whole deck's content fits in one (un-truncated) response.
MINS_PER_SLIDE     = 6
MAX_SLIDES         = 24
MIN_SLIDES         = 8
# At most this many slides may use a table; the rest render as bullets.
MAX_TABLES = 2

# Slides are generated one per call so each response is small and reliably valid.


class GenerateError(Exception):
    pass


def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise GenerateError("OPENROUTER_API_KEY not set in environment / .env")
    if not api_key.isascii():
        bad = [repr(c) for c in api_key if ord(c) > 127]
        raise GenerateError(
            f"OPENROUTER_API_KEY contains non-ASCII characters ({', '.join(bad)}) — "
            "this usually means a copy-paste turned a hyphen into an em-dash. "
            "Re-copy the key as plain text into .env."
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def _model() -> str:
    return os.environ.get("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-6")


def _load_prompt(filename: str) -> str:
    """Return a prompt-override file's content, or "" to use the built-in default.

    Stub files that contain only markdown headers and <!-- comments --> count as
    empty, so the placeholder prompt files don't get used as real prompts.
    """
    path = Path("content/prompts") / filename
    if not path.exists():
        return ""
    text = path.read_text()
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S)      # drop HTML comments
    body = re.sub(r"^\s*#.*$", "", body, flags=re.M).strip()  # drop md headings
    return text if len(body) > 30 else ""


def _block_map() -> dict:
    return LAYOUTS.get("block_to_layout", {})


def _call_llm(client: OpenAI, system: str, user: str, max_tokens: int = 2000,
              temperature: float = 0.5) -> str:
    response = client.chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _extract_json(raw: str):
    """Parse JSON from an LLM response, tolerating fences and surrounding prose.

    Handles: plain JSON, ```json fenced blocks, and JSON embedded in explanatory
    text (slices from the first [ or { to its matching last bracket). Works for
    both arrays (outline) and objects (spec). Raises GenerateError if empty.
    """
    if not raw or not raw.strip():
        raise GenerateError("LLM returned an empty response")
    s = raw.strip()

    # strip markdown code fences anywhere (```json ... ``` or ``` ... ```)
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s).strip()

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # slice from the first opening bracket to the matching last one (drops prose)
    candidates = [i for i in (s.find("["), s.find("{")) if i != -1]
    if candidates:
        start = min(candidates)
        close = "]" if s[start] == "[" else "}"
        end = s.rfind(close)
        if end > start:
            sliced = s[start:end + 1]
            try:
                return json.loads(sliced)
            except json.JSONDecodeError:
                s = sliced  # hand the trimmed JSON to the repairer below

    # last resort: repair malformed JSON (unescaped quotes, trailing commas, etc.),
    # which LLMs emit intermittently. json-repair never raises — it returns a
    # best-effort structure, or "" if nothing usable was found.
    from json_repair import repair_json
    repaired = repair_json(s, return_objects=True)
    if repaired in ("", None, [], {}):
        raise json.JSONDecodeError("could not parse or repair JSON from response", s, 0)
    return repaired


def _validate(spec: dict) -> list[str]:
    errors = []
    try:
        jsonschema.validate(spec, SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(f"at {list(e.absolute_path)}: {e.message}")
    return errors


def _parse_minutes(duration_str: str) -> int:
    digits = "".join(c for c in str(duration_str) if c.isdigit())[:4]
    try:
        return int(digits) if digits else 120
    except ValueError:
        return 120


def _slide_count(minutes: int) -> int:
    return max(MIN_SLIDES, min(MAX_SLIDES, round(minutes / MINS_PER_SLIDE)))


# ---------------------------------------------------------------------------
# Stage 1 — outline
# ---------------------------------------------------------------------------

_OUTLINE_SYSTEM = """You are an expert instructional designer.
Given training metadata, produce a slide-by-slide outline.
Return a JSON object of the form: {"outline": [ {"block": "...", "title": "...", "time_minutes": <int>}, ... ]}
where block is one of kickoff|theory|example|exercise|wrapup.
Rules:
- Follow this arc without exception: kickoff → (theory → example)+ → exercise → wrapup
- time_minutes values must sum exactly to the total duration
- Kickoff and wrapup: 5–10 min each. Exercises: at least 20 min total.
- Return ONLY the JSON object, no prose, no markdown fences."""


def _outline_user(meta: dict, slide_count: int, minutes: int) -> str:
    return f"""Generate a {slide_count}-slide outline for:

Topic: {meta['topic']}
Audience: {meta['audience']}
Level: {meta['level']}
Duration: {minutes} minutes
Objective: {meta['objective']}

Produce exactly {slide_count} slides. time_minutes values must sum to {minutes}.
Return a JSON object: {{"outline": [ ... ]}}"""


def _generate_outline(client: OpenAI, meta: dict) -> list[dict]:
    minutes     = _parse_minutes(meta["duration"])
    slide_count = _slide_count(minutes)
    system      = _load_prompt("outline_system.md") or _OUTLINE_SYSTEM
    user        = _outline_user(meta, slide_count, minutes)

    raw = _call_llm(client, system, user, max_tokens=4000, temperature=0.3)
    try:
        outline = _extract_json(raw)
    except json.JSONDecodeError:
        repair = (
            f"Your response was not valid JSON. Return only the JSON array, no prose, "
            f"starting with [ and ending with ].\n\nPrevious response:\n{raw}"
        )
        raw = _call_llm(client, system, repair, max_tokens=4000, temperature=0.2)
        try:
            outline = _extract_json(raw)
        except json.JSONDecodeError as e:
            raise GenerateError(f"Outline call returned invalid JSON after retry: {e}")

    # the model sometimes wraps the array in an object, e.g. {"outline": [...]}
    if isinstance(outline, dict):
        for key in ("outline", "slides", "items", "plan", "training"):
            if isinstance(outline.get(key), list):
                outline = outline[key]
                break
        else:
            lists = [v for v in outline.values() if isinstance(v, list)]
            outline = lists[0] if lists else None

    if not isinstance(outline, list) or not outline:
        raise GenerateError(f"Outline call returned no usable slide list (got {type(outline).__name__})")
    return outline


# ---------------------------------------------------------------------------
# Stage 2 — content
# ---------------------------------------------------------------------------

_CONTENT_SYSTEM = """You are an expert instructional designer writing slide content.

For EACH slide produce an object with exactly these keys:
- "block": one of kickoff|theory|example|exercise|wrapup (use the one given)
- "title": a short slide title
- "bullets": array of up to 5 short lines (~12 words each)
- "table": almost always null. Use a table ONLY when the content is truly tabular
  (a side-by-side comparison or a columned framework). Most slides must be bullets,
  not tables. A table replaces the bullets on that slide.
- "notes": object with ALL five keys, each 1-2 sentences:
    "aim", "time", "instructions", "reflective_q", "debrief"

Make content specific to the topic and audience — not generic filler.
Return ONLY valid JSON, no prose, no markdown fences."""


def _slides_user(meta: dict, chunk: list[dict], start: int) -> str:
    """User message asking for content for one chunk of slides."""
    lines = []
    for j, item in enumerate(chunk):
        item = item if isinstance(item, dict) else {}
        block = str(item.get("block") or item.get("type") or _DEFAULT_BLOCK).lower()
        title = item.get("title") or item.get("name") or "Untitled"
        mins = item.get("time_minutes", item.get("minutes", "?"))
        lines.append(f"{start + j + 1}. block={block} | title={title} | ~{mins} min")
    body = "\n".join(lines)
    return f"""Write slide content for these {len(chunk)} slides of a training.

Topic: {meta['topic']}
Audience: {meta['audience']}
Level: {meta['level']}
Objective: {meta['objective']}

Slides (keep the given block; you may refine the title):
{body}

Return ONLY JSON: {{"slides": [ <one object per slide, in order> ]}}"""


def _bites_user(meta: dict) -> str:
    return f"""Write two short participant documents for this training, as markdown strings.

Topic: {meta['topic']}
Audience: {meta['audience']}
Level: {meta['level']}
Objective: {meta['objective']}

- prebite: a short preparation task before the session (article to read, tool to install, or a reflection question)
- postbite: a follow-up after the session (reflection questions, an assignment, or further reading)

Return ONLY JSON: {{"prebite": "<markdown>", "postbite": "<markdown>"}}"""


_VALID_BLOCKS = {"kickoff", "theory", "example", "exercise", "wrapup"}
_DEFAULT_BLOCK = "theory"

# Fallbacks so a slide is always schema-valid even if the model omits a note field.
_NOTE_DEFAULTS = {
    "aim":          "(add the aim of this slide)",
    "time":         "5 minutes",
    "instructions": "(add facilitation instructions)",
    "reflective_q": "(add a reflective question)",
    "debrief":      "(add a one-line debrief)",
}


def _to_markdown(value) -> str:
    """Coerce a prebite/postbite value into a readable markdown string.

    The model sometimes returns these as structured objects/lists instead of a
    string; render them rather than failing schema validation.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(f"- {_to_markdown(v)}" for v in value)
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if isinstance(v, (list, dict)):
                lines.append(f"**{k}**\n{_to_markdown(v)}")
            else:
                lines.append(f"**{k}**: {v}")
        return "\n\n".join(lines)
    return str(value) if value is not None else ""


def _normalize_spec(spec: dict, meta: dict) -> None:
    """Make the whole spec schema-valid in code rather than relying on the LLM.

    Sets canonical meta, fills layout from block (we own that mapping), defaults
    unknown blocks, coerces bullets/table shapes, and renders prebite/postbite to
    strings. Mutates spec in place — this removes the need for an expensive
    LLM schema-repair round-trip.
    """
    spec["meta"] = meta
    block_map = _block_map()
    default_layout = block_map.get(_DEFAULT_BLOCK, "Title and Content")

    slides = spec.get("slides")
    slides = slides if isinstance(slides, list) else []
    spec["slides"] = [s for s in slides if isinstance(s, dict)]
    for slide in spec["slides"]:
        block = str(slide.get("block", "")).lower().strip()
        if block not in _VALID_BLOCKS:
            block = _DEFAULT_BLOCK
        slide["block"] = block
        slide["layout"] = block_map.get(block, default_layout)

        slide["title"] = str(slide.get("title") or "Untitled").strip() or "Untitled"

        bullets = slide.get("bullets")
        if not isinstance(bullets, list):
            slide["bullets"] = [str(bullets)] if bullets else []
        else:
            slide["bullets"] = [str(b) for b in bullets]

        table = slide.get("table")
        if (isinstance(table, dict) and isinstance(table.get("headers"), list)
                and isinstance(table.get("rows"), list)):
            slide["table"] = {
                "headers": [str(h) for h in table["headers"]],
                "rows": [[str(c) for c in row] for row in table["rows"]
                         if isinstance(row, list)],
            }
        else:
            slide["table"] = None

        # guarantee a notes dict with all 5 required fields as non-empty strings
        notes = slide.get("notes")
        notes = notes if isinstance(notes, dict) else {}
        slide["notes"] = {
            field: (str(notes.get(field) or "").strip() or default)
            for field, default in _NOTE_DEFAULTS.items()
        }

    # Tables replace the bullet content on a slide (the deck engine shows a table
    # OR bullets, not both), and the model tends to over-produce them. Keep at most
    # MAX_TABLES, only on theory/example slides; drop the rest so bullets render.
    kept = 0
    for slide in spec["slides"]:
        if slide["table"] is not None:
            if slide["block"] in ("theory", "example") and kept < MAX_TABLES:
                kept += 1
            else:
                slide["table"] = None

    spec["prebite"] = _to_markdown(spec.get("prebite")) or "(see session brief)"
    spec["postbite"] = _to_markdown(spec.get("postbite")) or "(see session follow-up)"


def _assign_blocks(n: int) -> list[str]:
    """Assign the didactic arc to n slides by position, so all five blocks are
    always present regardless of how the outline model labels things:
    first = kickoff, last = wrapup, the one before last = exercise, and the
    middle alternates theory / example (starting and ending on theory)."""
    blocks = ["theory"] * n
    if n >= 1:
        blocks[0] = "kickoff"
    if n >= 2:
        blocks[-1] = "wrapup"
    if n >= 3:
        blocks[-2] = "exercise"
    for i in range(1, max(1, n - 2)):
        blocks[i] = "theory" if i % 2 == 1 else "example"
    return blocks


def _slides_from_response(part) -> list:
    """Pull the slide list out of a content response of varying shape."""
    if isinstance(part, list):
        return part
    if isinstance(part, dict):
        if isinstance(part.get("slides"), list):
            return part["slides"]
        # a bare single-slide object (model often drops the {"slides": [...]} wrapper
        # when asked for one slide) — recognise it before grabbing any inner list
        if any(k in part for k in ("title", "notes", "block", "bullets")):
            return [part]
        lists = [v for v in part.values() if isinstance(v, list)]
        if lists:
            return lists[0]
    return []


def _generate_one_slide(client: OpenAI, system: str, meta: dict, item: dict, idx: int) -> dict:
    """Generate a single slide. One slide per call keeps each response small, so
    malformed JSON is rare; retry once, then fall back to the outline item so we
    always return a usable slide and never drop one."""
    for attempt in range(2):
        try:
            raw = _call_llm(client, system, _slides_user(meta, [item], idx),
                            max_tokens=2000, temperature=0.3 if attempt else 0.5)
            slides = _slides_from_response(_extract_json(raw))
            if slides and isinstance(slides[0], dict) and slides[0].get("title"):
                return slides[0]
        except (json.JSONDecodeError, GenerateError):
            continue
    # fallback: build a minimal slide from the outline item (notes filled by normalize)
    kp = item.get("key_points")
    return {
        "title": item.get("title", "Untitled"),
        "bullets": kp if isinstance(kp, list) else [],
    }


def _generate_content(client: OpenAI, meta: dict, outline: list[dict]) -> dict:
    """Generate content one slide per call (reliable full notes; no dropped slides),
    fetch prebite/postbite separately, and assign the block by position so the
    didactic arc is guaranteed regardless of model output."""
    system = _load_prompt("generate_system.md") or _CONTENT_SYSTEM

    # we own the arc: assign blocks by position and attach to each outline item so
    # the content prompt asks for the right block, regardless of the outline's shape
    blocks = _assign_blocks(len(outline))
    items = []
    for i, item in enumerate(outline):
        it = dict(item) if isinstance(item, dict) else {"title": str(item)}
        it["block"] = blocks[i]
        items.append(it)

    all_slides = [_generate_one_slide(client, system, meta, it, i) for i, it in enumerate(items)]

    # prebite + postbite in their own small, reliable call
    prebite = postbite = ""
    try:
        bites = _extract_json(_call_llm(
            client, "You write concise training prep documents. Return only JSON.",
            _bites_user(meta), max_tokens=2000))
        if isinstance(bites, dict):
            prebite, postbite = bites.get("prebite", ""), bites.get("postbite", "")
    except (json.JSONDecodeError, GenerateError):
        pass  # normalization supplies a safe fallback

    spec = {"meta": meta, "slides": all_slides, "prebite": prebite, "postbite": postbite}

    # stamp the positional block onto each slide — guarantees the arc
    for idx, slide in enumerate(spec["slides"]):
        if isinstance(slide, dict) and idx < len(blocks):
            slide["block"] = blocks[idx]

    _normalize_spec(spec, meta)
    errors = _validate(spec)
    if errors:
        raise GenerateError(f"Generated spec failed schema validation after normalization: {errors}")
    return spec


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_spec(meta: dict) -> dict:
    """
    Two-stage LLM pipeline: meta -> full training spec matching training_spec.schema.json.
    Stage 1: outline (titles + blocks + timing).
    Stage 2: content (bullets, tables, speaker notes, pre/post-bite).
    Raises GenerateError on unrecoverable failure.
    """
    # coerce every value to a string so numeric input (e.g. duration 90) satisfies
    # the schema and never crashes string handling downstream
    meta    = {k: str(v).strip() for k, v in meta.items()}
    client  = _get_client()
    outline = _generate_outline(client, meta)
    spec    = _generate_content(client, meta, outline)
    return spec


if __name__ == "__main__":
    import sys
    meta_path = sys.argv[1] if len(sys.argv) > 1 else "schema/sample_spec.json"
    raw       = json.loads(Path(meta_path).read_text())
    meta      = raw.get("meta", raw)
    spec      = generate_spec(meta)
    out_path  = "output/generated_spec.json"
    Path("output").mkdir(exist_ok=True)
    Path(out_path).write_text(json.dumps(spec, indent=2))
    print(f"Written: {out_path}")
