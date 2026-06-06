# Maverx AI Training Builder

Answer 5 questions → get a complete, on-brand training: an editable **PowerPoint deck**
(Maverx house style, speaker notes on every slide) plus **pre-bite** and **post-bite** docs.
You can also choose to get the raw **JSON spec** instead of the deck.

## Run it (Docker Compose)

```bash
cp .env.example .env          # then set OPENROUTER_API_KEY=sk-or-v1-...
docker compose up --build     # open http://localhost:8501
```

Stop with `Ctrl+C` (or `docker compose down`).

## Use it

1. Open http://localhost:8501
2. Answer the 5 questions (topic, audience, level, duration, objective).
   Vague answers get a follow-up.
3. Choose **PowerPoint deck (.pptx)** or **Training spec (JSON)**.
4. Click **Generate** (takes ~1–2 min) and download the files.

## Config

| Variable | Required | Default |
|----------|----------|---------|
| `OPENROUTER_API_KEY` | yes | — |
| `OPENROUTER_MODEL` | no | `anthropic/claude-sonnet-4-6` |

## How it works

React UI → FastAPI (`backend/app.py`) → content pipeline (`content/`) builds the training
spec → deck engine (`engine/`) renders the `.pptx` + `.docx`. To use a different brand,
swap `master/maverx_master.pptx` and update `schema/layouts.json`.
