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

import re

REQUIRED_FIELDS = ["topic", "audience", "level", "duration", "objective"]

# Schema requires exactly these three values for level
LEVEL_ENUM = ["beginner", "intermediate", "advanced"]

# Words users type that map to each canonical level
LEVEL_ALIASES = {
    "beginner":     ["beginner", "begin", "no experience", "no prior", "novice", "new",
                     "never", "zero", "none", "basic", "starter", "entry"],
    "intermediate": ["intermediate", "some experience", "some", "moderate", "familiar",
                     "worked with", "used before", "average", "mid"],
    "advanced":     ["advanced", "expert", "confident", "experienced", "senior",
                     "professional", "practitioner", "deep", "extensive"],
}

QUESTIONS = {
    "topic":     "What is the topic or skill to be trained? (e.g. 'Excel pivot tables', 'Conflict resolution')",
    "audience":  "Who is the target audience? (e.g. 'junior sales reps', 'team managers in logistics')",
    "level":     "What is the knowledge level of participants? (beginner / intermediate / advanced)",
    "duration":  "How long is the training in minutes? (e.g. '90', '180', '240')",
    "objective": "What is the primary learning objective? What should participants be able to DO after the session?",
}

# Single-word "filler" tokens. An answer is vague only if EVERY meaningful word
# in it is one of these (so "team" is vague, but "team leads" is not).
# duration is handled separately (must contain a number); level via _normalize_level.
VAGUE_TOKENS = {
    "topic":     {"something", "stuff", "things", "thing", "topic", "training", "course", "anything"},
    "audience":  {"everyone", "everybody", "anyone", "anybody", "people", "team", "teams",
                  "staff", "employees", "employee", "users", "user", "folks", "group", "everybody"},
    "objective": {"learn", "learning", "understand", "understanding", "know", "knowing",
                  "improve", "improving", "better", "stuff", "things", "grow"},
}

# Stripped before vagueness analysis so "the team" reduces to {"team"}.
STOPWORDS = {"the", "a", "an", "our", "my", "your", "their", "of", "for", "to", "in", "on",
             "at", "and", "or", "with", "some", "that", "this", "these", "those", "is",
             "are", "be", "will", "can", "they", "it", "about", "all", "more", "how", "what"}

FOLLOW_UPS = {
    "topic":     "That's a bit broad — could you be more specific? For example: 'negotiation techniques', 'Power BI dashboards', or 'writing effective emails'.",
    "audience":  "Could you narrow that down? For example: 'marketing coordinators with 0–2 years experience' or 'senior project managers'.",
    "level":     "Please choose one: beginner (no prior knowledge), intermediate (some experience), or advanced (confident practitioners).",
    "duration":  "Please give an exact number of minutes — for example: 90, 120, or 180.",
    "objective": "Try completing this sentence: 'After this training, participants will be able to...' — be specific about a skill or action.",
}


def _normalize_level(value) -> str | None:
    """Map free-text level answer to schema enum. Returns None if unrecognisable."""
    v = str(value).lower().strip()
    if v in LEVEL_ENUM:
        return v
    for canonical, aliases in LEVEL_ALIASES.items():
        if any(alias in v for alias in aliases):
            return canonical
    return None


def _is_vague(field: str, value) -> bool:
    # tolerate non-string input (e.g. duration entered as the number 90, not "90")
    v = str(value).lower().strip()
    if field == "level":
        # vague = cannot be normalised to the enum
        return _normalize_level(value) is None
    if field == "duration":
        # a usable duration must contain a number; "a few hours" doesn't, "90" / "90 min" do.
        # Checked before the generic length rule so short numbers like "90" are accepted.
        return not any(ch.isdigit() for ch in v)
    if len(v) < 3:  # reject empty / single-char answers, allow short valid ones (HR, QA)
        return True
    # topic / audience / objective: vague only if every meaningful word is a filler token
    tokens = [t for t in re.split(r"[^a-z0-9]+", v) if t and t not in STOPWORDS]
    if not tokens:
        return True
    filler = VAGUE_TOKENS.get(field, set())
    return all(t in filler for t in tokens)


def _first_field_needing_input(state: dict) -> tuple[str | None, str | None]:
    """Walk fields in order; return the first that is missing or vague.

    Interleaving missing+vague per field (rather than all-missing-then-all-vague)
    means a vague answer is challenged immediately, not after every field is filled.
    """
    for field in REQUIRED_FIELDS:
        val = state.get(field, "")
        if not val:
            return field, "missing"
        if _is_vague(field, val):
            return field, "vague"
    return None, None


def _build_meta(state: dict) -> dict:
    """Return meta dict with all values as strings and level normalized to the enum.

    Coercing to str means a duration entered as the number 90 is stored as "90",
    so it satisfies the schema (which requires strings) without the user needing quotes.
    """
    meta = {field: str(state[field]).strip() for field in REQUIRED_FIELDS}
    meta["level"] = _normalize_level(state["level"]) or meta["level"]
    return meta


def assess_intake(state: dict) -> dict:
    """
    Given current intake state dict, returns next question or ready signal.
    state keys are the REQUIRED_FIELDS; values are what the user has answered so far.

    A field that is missing gets its base question; a field that is present but
    vague gets its follow-up question — challenged immediately, in field order.
    Never returns "ready" until all five fields are present and specific enough,
    which is how the system refuses to generate on incomplete intake.
    """
    field, reason = _first_field_needing_input(state)
    if field:
        return {
            "status": "question",
            "field":  field,
            "text":   QUESTIONS[field] if reason == "missing" else FOLLOW_UPS[field],
        }

    return {
        "status": "ready",
        "meta":   _build_meta(state),
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
