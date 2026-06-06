# Maverx AI Training Builder

From a one-sentence idea to a complete, structured training spec in Maverx house style —
through a guided 5-question intake. A React UI talks to a FastAPI backend that runs the
content pipeline and returns an editable training spec (slides, speaker notes, pre/post-bite).

---

## What it does

1. Asks 5 targeted intake questions (with follow-ups for vague answers, refuses until complete)
2. Generates a training that follows the Maverx didactic arc:
   **kickoff → theory → example → exercise → wrap-up**
3. Produces a full training **spec**: per-slide title, bullets, tables, and speaker notes
   with all 5 fields (aim, time, instructions, reflective question, debrief)
4. Produces a **pre-bite** (prep) and **post-bite** (follow-up) document
5. Renders an **editable `.pptx`** in Maverx house style (real master layouts, speaker
   notes on every slide, real tables) plus `.docx` pre/post-bite

**Output toggle:** before generating, choose **PowerPoint deck (.pptx)** to get the editable
deck + `.docx` docs, or **Training spec (JSON)** to get just the structured `spec.json` +
`prebite.md` / `postbite.md`.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- An [OpenRouter](https://openrouter.ai) API key (the content pipeline uses it)

---

## Run it with Docker Compose

```bash
# 1. Add your API key
cp .env.example .env
#    then edit .env and set:
#      OPENROUTER_API_KEY=sk-or-v1-...your real key...
#      OPENROUTER_MODEL=anthropic/claude-sonnet-4-6     # default; any OpenRouter model id works

# 2. Build and start
docker compose up --build

# 3. Open the app
#    http://localhost:8501
```

To stop: `Ctrl+C`, or `docker compose down`.
To rebuild after code changes: `docker compose up --build`.

---

## Usage

1. Open **http://localhost:8501**
2. Answer the 5 questions in the chat (topic, audience, level, duration, objective).
   Vague answers get a follow-up — that's intentional.
3. Pick the output mode: **PowerPoint deck (.pptx)** or **Training spec (JSON)**.
4. Click **Generate training deck**. Generation takes ~1–2 minutes (the pipeline writes
   one slide at a time for reliability).
5. Download the results — `.pptx` + `prebite.docx` + `postbite.docx` (PowerPoint mode),
   or `spec.json` + `prebite.md` + `postbite.md` (JSON mode).

---

## Architecture

```
React UI (frontend/maverx, served as static files)
   │  POST /api/generate  { topic, audience, level, duration, objective }
   ▼
FastAPI backend (backend/app.py)
   │
   ├── content/intake.py     — 5-question gate, vagueness follow-ups  (POST /api/assess)
   └── content/generate.py   — two-stage LLM pipeline via OpenRouter
                                outline → per-slide content → validated training spec
   ▼
Training spec JSON  (meta · slides · prebite · postbite)
   ▼
engine/ (Person A) — build_pptx + build_bites turn the spec into editable
                     .pptx (Team19 master layouts) + .docx pre/post-bite
```

The contract between the pipeline and the deck engine is documented in
`schema/CONTRACT_FOR_PERSON_A.md`, with a real sample in `schema/sample_generated_spec.json`.

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key used for content generation |
| `OPENROUTER_MODEL` | No | Model id (default `anthropic/claude-sonnet-4-6`); swap for a cheaper one to save cost on test runs |

---

## Run the backend without Docker (optional)

```bash
pip install -r requirements.txt
cp .env.example .env   # add your key
uvicorn backend.app:app --host 0.0.0.0 --port 8501
# open http://localhost:8501
```

---

## Swapping the house-style template

The deck engine builds onto the Maverx master at `master/maverx_master.pptx`. To use a
different brand, replace that file and update `schema/layouts.json` → `block_to_layout`
with layout names from the new master (`python engine/layouts_report.py <master.pptx>`
lists them). The content pipeline is template-agnostic.

---

## Repo layout

| Path | What |
|------|------|
| `frontend/maverx/` | React UI (intake wizard + live brief + downloads) |
| `backend/app.py` | FastAPI: serves the UI + `/api/generate`, `/api/assess`, `/api/health` |
| `content/` | Intake + LLM content pipeline (Person B) |
| `engine/` | PPTX / docx renderer (Person A) — wired into `/api/generate` |
| `schema/` | Training-spec JSON schema, layout map, sample, engine contract |
| `master/` | Maverx master template + brand assets |
| `STYLE_CHECKLIST.md` | House-style QA checklist |
| `MASTER_PLAN.md` | Team plan and role split |
