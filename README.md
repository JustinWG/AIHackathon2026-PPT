# Maverx AI Training Builder

From a one-sentence idea to a complete, editable PowerPoint deck in Maverx house style —
in under 10 minutes.

---

## What it does

1. Asks 5 targeted intake questions (with follow-ups for vague answers)
2. Refuses to generate until intake is complete
3. Generates a structured training deck following the Maverx didactic model:
   **kickoff → theory → example → exercise → wrap-up**
4. Produces a fully editable `.pptx` using the Maverx master template
5. Includes speaker notes on every slide (aim, time, instructions, reflective question, debrief)
6. Produces a pre-session preparation document and a post-session follow-up document

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- An [OpenRouter](https://openrouter.ai) API key
- The Maverx master template file (see Setup below)

---

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd AIHackathon2026-PPT

# 2. Add your API key
cp .env.example .env
# Edit .env and replace your_key_here with your actual OPENROUTER_API_KEY

# 3. Build and run
docker compose up --build

# 4. Open in browser
# http://localhost:8501
```

---

## Usage

1. Open `http://localhost:8501`
2. Answer the intake questions in the chat interface
3. If your answer is vague, the system will ask a follow-up — this is intentional
4. Once all 5 questions are answered, click **Generate Training**
5. Download your `.pptx`, `prebite.docx`, and `postbite.docx`

---

## How to swap the template

The pipeline is template-agnostic. To use a different branded template:

1. Replace `master/maverx_master.pptx` with any `.pptx` master file
2. Run `python engine/layouts_report.py master/your_master.pptx` to see its layout names
3. Update `schema/layouts.json` → `block_to_layout` with the correct layout names
4. Restart the app — no other changes needed

---

## Architecture

```
Streamlit UI (app/app.py)
  │
  ├── Intake gate (content/intake.py)
  │     Rule-based: 5 required fields, vagueness detection, follow-up questions
  │
  ├── Spec generator (content/generate.py)
  │     Two LLM calls via OpenRouter → validated JSON training spec
  │
  ├── PPTX assembler (engine/build_pptx.py)
  │     python-pptx: injects content into master template layouts
  │
  └── Docs builder (engine/build_docs.py)
        python-docx: pre-bite and post-bite as editable .docx
```

All content flows through a typed JSON contract (`schema/training_spec.schema.json`).
The LLM never writes PPTX — it writes JSON that the assembler consumes.

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `OPENROUTER_MODEL` | No | Model to use via OpenRouter (default: `google/gemini-3.5-flash`) |

---

## Running without Docker

```bash
pip install -r requirements.txt
cp .env.example .env  # add your API key
streamlit run app/app.py
```

---

## Dependencies

See `requirements.txt` for pinned versions.
