"""
B1 — Intake logic (Person B).

Public API (do not change signature without team sync):
    assess_intake(state: dict) -> dict

Returns one of:
  { "status": "question", "text": "...", "field": "audience" }
  { "status": "ready",    "meta": { topic, audience, level, duration, objective } }
  { "status": "refuse",   "text": "...", "missing": ["field", ...] }

C calls this per Streamlit message. C owns the UI loop and session_state.
"""

REQUIRED_FIELDS = ["topic", "audience", "level", "duration", "objective"]

QUESTIONS = {
    "topic":     "What is the topic or skill to be trained? (e.g. 'Excel pivot tables', 'Conflict resolution')",
    "audience":  "Who is the target audience? (e.g. 'junior sales reps', 'team managers in logistics')",
    "level":     "What is the knowledge level of participants? (beginner / intermediate / advanced)",
    "duration":  "How long is the training in minutes? (e.g. '90', '180', '240')",
    "objective": "What is the primary learning objective? What should participants be able to DO after the session?",
}

VAGUE_PATTERNS = {
    "topic":     ["something", "stuff", "things", "topic", "training", "course"],
    "audience":  ["everyone", "anybody", "people", "team", "staff", "employees", "users"],
    "level":     [],
    "duration":  ["a while", "some time", "half a day", "a day", "few hours", "a few"],
    "objective": ["learn", "understand", "know", "get better", "improve", "stuff"],
}

FOLLOW_UPS = {
    "topic":     "That's a bit broad — could you be more specific? For example: 'negotiation techniques', 'Power BI dashboards', or 'writing effective emails'.",
    "audience":  "Could you narrow that down? For example: 'marketing coordinators with 0–2 years experience' or 'senior project managers'.",
    "level":     "Please choose one: beginner (no prior knowledge), intermediate (some experience), or advanced (confident practitioners).",
    "duration":  "Please give an exact number of minutes — for example: 90, 120, or 180.",
    "objective": "Try completing this sentence: 'After this training, participants will be able to...' — be specific about a skill or action.",
}


def _is_vague(field: str, value: str) -> bool:
    value_lower = value.lower().strip()
    if len(value_lower) < 5:
        return True
    return any(pattern in value_lower for pattern in VAGUE_PATTERNS.get(field, []))


def _next_missing_field(state: dict) -> str | None:
    for field in REQUIRED_FIELDS:
        if field not in state or not state[field]:
            return field
    return None


def _next_vague_field(state: dict) -> str | None:
    for field in REQUIRED_FIELDS:
        val = state.get(field, "")
        if val and _is_vague(field, val):
            return field
    return None


def assess_intake(state: dict) -> dict:
    """
    Given current intake state dict, returns next question, ready signal, or refuse.
    state keys are the REQUIRED_FIELDS; values are what the user has answered so far.
    """
    missing_field = _next_missing_field(state)
    if missing_field:
        return {
            "status": "question",
            "field":  missing_field,
            "text":   QUESTIONS[missing_field],
        }

    vague_field = _next_vague_field(state)
    if vague_field:
        return {
            "status": "question",
            "field":  vague_field,
            "text":   FOLLOW_UPS[vague_field],
        }

    missing = [f for f in REQUIRED_FIELDS if not state.get(f)]
    if missing:
        return {
            "status":  "refuse",
            "missing": missing,
            "text":    f"I can't generate the training yet — still need: {', '.join(missing)}.",
        }

    return {
        "status": "ready",
        "meta": {field: state[field] for field in REQUIRED_FIELDS},
    }


if __name__ == "__main__":
    # CLI walkthrough for testing without Streamlit
    state: dict = {}
    print("=== Intake (CLI test mode) ===\n")
    while True:
        result = assess_intake(state)
        if result["status"] == "ready":
            print("\n✓ Intake complete:")
            for k, v in result["meta"].items():
                print(f"  {k}: {v}")
            break
        elif result["status"] == "refuse":
            print(f"\n✗ Refused: {result['text']}")
            break
        else:
            answer = input(f"{result['text']}\n> ").strip()
            state[result["field"]] = answer
