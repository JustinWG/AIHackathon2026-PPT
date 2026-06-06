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

# Target ~1 slide per 5 minutes — ~18 slides for 90 min, ~24 for 2 hrs, ~36 for 3 hrs.
# Capped at 40 to keep JSON within token limits.
MINS_PER_SLIDE     = 5
MAX_SLIDES         = 40
MIN_SLIDES         = 8
CONTENT_MAX_TOKENS = 8000  # a 40-slide JSON with full notes is ~6k tokens


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
    path = Path("content/prompts") / filename
    return path.read_text() if path.exists() and path.stat().st_size > 50 else ""


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

    # fall back: slice from the first opening bracket to the matching last one
    candidates = [i for i in (s.find("["), s.find("{")) if i != -1]
    if not candidates:
        raise json.JSONDecodeError("no JSON value found in response", s, 0)
    start = min(candidates)
    close = "]" if s[start] == "[" else "}"
    end = s.rfind(close)
    if end <= start:
        raise json.JSONDecodeError("no matching closing bracket in response", s, 0)
    return json.loads(s[start:end + 1])


def _validate(spec: dict) -> list[str]:
    errors = []
    try:
        jsonschema.validate(spec, SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(str(e.message))
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
Given training metadata, produce a slide-by-slide outline as a JSON array.
Each item: {"block": "kickoff|theory|example|exercise|wrapup", "title": "...", "time_minutes": <int>}
Rules:
- Follow this arc without exception: kickoff → (theory → example)+ → exercise → wrapup
- time_minutes values must sum exactly to the total duration
- Kickoff and wrapup: 5–10 min each. Exercises: at least 20 min total.

OUTPUT FORMAT (critical):
- Output ONLY the JSON array. Nothing before it, nothing after it.
- No prose, no explanation, no markdown code fences.
- Your response must start with the character [ and end with the character ]."""


def _outline_user(meta: dict, slide_count: int, minutes: int) -> str:
    return f"""Generate a {slide_count}-slide outline for:

Topic: {meta['topic']}
Audience: {meta['audience']}
Level: {meta['level']}
Duration: {minutes} minutes
Objective: {meta['objective']}

Produce exactly {slide_count} slides. time_minutes values must sum to {minutes}."""


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

    if not isinstance(outline, list):
        raise GenerateError(f"Outline call returned unexpected type: {type(outline)}")
    return outline


# ---------------------------------------------------------------------------
# Stage 2 — content
# ---------------------------------------------------------------------------

def _content_system(block_map: dict) -> str:
    layout_list = "\n".join(f"  {block}: {layout}" for block, layout in block_map.items())
    return f"""You are an expert instructional designer. Fill a slide outline into a complete training spec.

LAYOUT MAP — use ONLY these layout values:
{layout_list}

RULES:
1. Every slide must have all 5 speaker note fields: aim, time, instructions, reflective_q, debrief
2. time in notes must match the outline's time_minutes (write as "X minutes")
3. At least one slide must use a table where it genuinely aids understanding
4. bullets is always an array (never null, can be empty []); table is null or a valid table object
5. Make content specific to the topic and audience — not generic filler
6. Return ONLY valid JSON matching the schema — no prose, no markdown fences

REQUIRED JSON STRUCTURE:
{{
  "meta": {{}},
  "slides": [
    {{
      "layout": "<from layout map>",
      "block": "kickoff|theory|example|exercise|wrapup",
      "title": "",
      "bullets": [""],
      "table": null,
      "notes": {{
        "aim": "", "time": "", "instructions": "", "reflective_q": "", "debrief": ""
      }}
    }}
  ],
  "prebite": "<markdown>",
  "postbite": "<markdown>"
}}"""


def _content_user(meta: dict, outline: list[dict]) -> str:
    # Defensive: the outline is a planning aid; tolerate items with missing/oddly
    # named keys rather than crashing. The content system prompt re-enforces the arc.
    def _fmt(i: int, item: dict) -> str:
        if not isinstance(item, dict):
            return f"{i+1}. {item}"
        block = str(item.get("block") or item.get("type") or "").upper()
        title = item.get("title") or item.get("name") or "Untitled"
        mins = item.get("time_minutes", item.get("minutes", "?"))
        return f"{i+1}. [{block}] {title} ({mins} min)"

    outline_text = "\n".join(_fmt(i, item) for i, item in enumerate(outline))
    return f"""Fill this outline into a complete training spec JSON.

Metadata:
  Topic: {meta['topic']}
  Audience: {meta['audience']}
  Level: {meta['level']}
  Duration: {meta['duration']}
  Objective: {meta['objective']}

Outline ({len(outline)} slides):
{outline_text}

Also generate:
- prebite: a short preparation task for participants before the session (article/reflection/install)
- postbite: a follow-up after the session (reflection questions, assignment, further reading)

Return the full spec JSON only."""


def _generate_content(client: OpenAI, meta: dict, outline: list[dict]) -> dict:
    block_map = _block_map()
    system    = _load_prompt("generate_system.md") or _content_system(block_map)
    user      = _content_user(meta, outline)

    raw = _call_llm(client, system, user, max_tokens=CONTENT_MAX_TOKENS)

    try:
        spec = _extract_json(raw)
    except json.JSONDecodeError as e:
        repair = (
            f"Your response was not valid JSON. Error: {e}\n\n"
            f"Return only the corrected JSON, no prose, no markdown fences.\n\n"
            f"Previous response:\n{raw}"
        )
        raw = _call_llm(client, system, repair, max_tokens=CONTENT_MAX_TOKENS)
        try:
            spec = _extract_json(raw)
        except json.JSONDecodeError as e2:
            raise GenerateError(f"LLM returned invalid JSON after retry: {e2}")

    # always use canonical intake meta — never trust what the LLM echoes back
    spec["meta"] = meta

    errors = _validate(spec)
    if errors:
        repair = (
            f"Your JSON had schema validation errors:\n{errors}\n\n"
            f"Fix them and return only the corrected JSON.\n\nPrevious response:\n{json.dumps(spec)}"
        )
        raw = _call_llm(client, system, repair, max_tokens=CONTENT_MAX_TOKENS)
        try:
            spec = _extract_json(raw)
        except json.JSONDecodeError as e:
            raise GenerateError(f"Schema repair returned invalid JSON: {e}")
        spec["meta"] = meta
        errors = _validate(spec)
        if errors:
            raise GenerateError(f"Generated spec failed schema validation after repair: {errors}")

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
