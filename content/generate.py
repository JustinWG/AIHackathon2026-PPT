"""
B2/B3 — Training spec generator (Person B).

Public API (do not change signature without team sync):
    generate_spec(meta: dict) -> dict

Raises GenerateError on unrecoverable failure.
"""
import json
import os
from pathlib import Path

from openai import OpenAI
import jsonschema
from dotenv import load_dotenv

load_dotenv()

SCHEMA = json.loads(Path("schema/training_spec.schema.json").read_text())
LAYOUTS = json.loads(Path("schema/layouts.json").read_text())


class GenerateError(Exception):
    pass


def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise GenerateError("OPENROUTER_API_KEY not set in environment / .env")
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def _load_prompt(filename: str) -> str:
    path = Path("content/prompts") / filename
    if path.exists():
        return path.read_text()
    return ""


def _block_to_layout_map() -> dict:
    return LAYOUTS.get("block_to_layout", {})


def _call_llm(client: OpenAI, system: str, user: str, model: str = "anthropic/claude-3.5-sonnet") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


def _extract_json(raw: str) -> dict:
    """Strip markdown fences if present, then parse JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(raw)


def _validate(spec: dict) -> list[str]:
    errors = []
    try:
        jsonschema.validate(spec, SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(str(e.message))
    return errors


def generate_spec(meta: dict) -> dict:
    """
    LLM pipeline: meta -> full training spec matching training_spec.schema.json.
    Raises GenerateError on unrecoverable failure.
    """
    client = _get_client()
    block_map = _block_to_layout_map()
    system_prompt = _load_prompt("generate_system.md") or _default_system(block_map)
    user_message = _build_user_message(meta, block_map)

    raw = _call_llm(client, system_prompt, user_message)

    try:
        spec = _extract_json(raw)
    except json.JSONDecodeError as e:
        # Retry once with repair instruction
        repair_msg = (
            f"Your previous response was not valid JSON. Error: {e}\n\n"
            f"Return only the corrected JSON, no prose, no markdown fences.\n\n"
            f"Previous response:\n{raw}"
        )
        raw = _call_llm(client, system_prompt, repair_msg)
        try:
            spec = _extract_json(raw)
        except json.JSONDecodeError as e2:
            raise GenerateError(f"LLM returned invalid JSON after retry: {e2}")

    errors = _validate(spec)
    if errors:
        raise GenerateError(f"Generated spec failed schema validation: {errors}")

    return spec


def _default_system(block_map: dict) -> str:
    layout_list = "\n".join(f"  - {block}: {layout}" for block, layout in block_map.items())
    return f"""You are an expert instructional designer. You generate complete, structured training specifications in JSON.

LAYOUT MAP — use ONLY these layout values for each block type:
{layout_list}

RULES:
1. Every training must follow this exact didactic arc: kickoff → theory → example → exercise → wrapup
2. Every slide must have all 5 speaker note fields: aim, time, instructions, reflective_q, debrief
3. Timing across all slides must sum to the stated duration in minutes
4. Use beginner-appropriate language when level is "beginner"
5. Return ONLY valid JSON matching the schema — no prose, no markdown fences, no explanation
6. bullets is always an array (can be empty []); table is either null or a valid table object
7. Slide count: approximately 1 slide per 4 minutes of training duration

REQUIRED JSON STRUCTURE:
{{
  "meta": {{ "topic": "", "audience": "", "level": "", "duration": "", "objective": "" }},
  "slides": [
    {{
      "layout": "<from layout map above>",
      "block": "kickoff|theory|example|exercise|wrapup",
      "title": "",
      "bullets": [""],
      "table": null,
      "notes": {{
        "aim": "", "time": "", "instructions": "", "reflective_q": "", "debrief": ""
      }}
    }}
  ],
  "prebite": "<markdown string>",
  "postbite": "<markdown string>"
}}"""


def _build_user_message(meta: dict, block_map: dict) -> str:
    duration_min = meta.get("duration", "120")
    try:
        minutes = int("".join(filter(str.isdigit, str(duration_min)[:4])))
    except ValueError:
        minutes = 120
    slide_count = max(8, round(minutes / 4))

    return f"""Generate a complete training specification for:

Topic: {meta['topic']}
Audience: {meta['audience']}
Knowledge level: {meta['level']}
Duration: {meta['duration']}
Primary learning objective: {meta['objective']}

Target approximately {slide_count} slides total. Distribute timing so all slides sum to {minutes} minutes.
At least one slide should use a table where it genuinely aids understanding (a framework, comparison, or checklist).
Make content specific to the topic and audience — not generic filler.
"""


if __name__ == "__main__":
    import sys
    intake_path = sys.argv[1] if len(sys.argv) > 1 else "schema/sample_spec.json"
    meta = json.loads(Path(intake_path).read_text()).get("meta")
    if not meta:
        print("Pass a file with a top-level 'meta' key, or a raw meta dict.")
        sys.exit(1)
    spec = generate_spec(meta)
    out_path = "output/generated_spec.json"
    Path("output").mkdir(exist_ok=True)
    Path(out_path).write_text(json.dumps(spec, indent=2))
    print(f"Written: {out_path}")
