# Person B — Content Pipeline

This folder is the brain of the app. It asks the user the right questions, then calls the AI to generate the full training structure.

---

## What this does in plain English

1. **Asks the user 5 questions** (intake)
   - What is the topic?
   - Who is the audience?
   - What is their knowledge level?
   - How long is the training?
   - What should participants be able to do after?

   If the answer is vague ("our team", "a few hours"), it asks again with a more specific follow-up. It refuses to move forward until all 5 answers are clear enough.

2. **Generates a training outline** (AI call 1)
   - Decides how many slides to make based on the duration (~1 slide per 5 minutes)
   - Lays out the arc: kick-off → theory → example → exercise → wrap-up
   - Distributes time across all slides so it adds up to the total duration

3. **Fills in all the slide content** (AI call 2)
   - Writes the title and bullet points for every slide
   - Adds a table where it genuinely helps (frameworks, comparisons, checklists)
   - Writes speaker notes for every slide with 5 fields:
     - **Aim** — what this slide is for
     - **Time** — how many minutes to spend
     - **Instructions** — what the trainer should say and do
     - **Reflective question** — a question to ask the audience
     - **Debrief** — how to close the slide
   - Writes a **pre-bite** — a short task for participants to do *before* the session
   - Writes a **post-bite** — a follow-up for participants to do *after* the session

4. **Hands the result to Person A** as a structured JSON file, which A then assembles into the actual PowerPoint.

---

## Files

| File | What it does |
|------|-------------|
| `intake.py` | The question-asking logic. Stateless — C calls it once per message. |
| `generate.py` | The AI pipeline. Two-stage: outline first, then content. |
| `prompts/outline_system.md` | Override the stage-1 prompt without touching Python. Leave empty to use the built-in default. |
| `prompts/generate_system.md` | Override the stage-2 prompt without touching Python. Leave empty to use the built-in default. |
| `prompts/intake_system.md` | Reference file if you want to add LLM-assisted vagueness detection. |

---

## How to run it standalone (for testing without the UI)

Make sure you have a `.env` file with your API key:

```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-sonnet-4-6
```

**Test the intake** (walks you through the 5 questions in the terminal):

```bash
docker compose run --rm app python content/intake.py
```

**Test the full generation** (reads meta from `schema/sample_spec.json`, generates a full spec, writes to `output/generated_spec.json`):

```bash
docker compose run --rm app python content/generate.py
```

---

## What goes in, what comes out

**In** — the 5 intake answers as a dict:
```json
{
  "topic": "Prompt Engineering for Marketing",
  "audience": "Marketing coordinators, no AI experience",
  "level": "beginner",
  "duration": "180 minutes",
  "objective": "Participants can write effective prompts using a structured framework"
}
```

**Out** — a full training spec (JSON), which Person A turns into a PowerPoint:
```json
{
  "meta": { ... },
  "slides": [
    {
      "layout": "Title Slide",
      "block": "kickoff",
      "title": "Welcome: Prompt Engineering for Marketers",
      "bullets": ["What you will be able to do today", "Agenda"],
      "table": null,
      "notes": {
        "aim": "Set expectations and create psychological safety.",
        "time": "10 minutes",
        "instructions": "Open with a show-of-hands: who has tried ChatGPT before?",
        "reflective_q": "What is one thing you hope to take away today?",
        "debrief": "Recap the objective and confirm the agenda is clear."
      }
    }
  ],
  "prebite": "## Before the Session\n\nRead this short article on AI prompting...",
  "postbite": "## After the Session\n\nReflect on these questions..."
}
```

---

## Key decisions made

- **Two AI calls, not one** — the outline call is short and cheap; it locks in timing and structure before the expensive content call. This prevents timing drift across 20+ slides and avoids JSON truncation.
- **Level is always normalized** — if a user types "no experience" or "newbie", it gets stored as `"beginner"` before the AI call. This prevents a schema crash downstream.
- **Model is configurable** — set `OPENROUTER_MODEL` in `.env`. Default is `claude-sonnet-4-6` (fast, cheap, great for structured JSON). Flip to `claude-opus-4-8` for the final demo run if you want richer prose.
- **Repair retries** — if the AI returns broken JSON or fails schema validation, it gets one automatic repair attempt before raising an error to the UI.
