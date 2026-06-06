# Maverx AI Training Builder — Master Plan
**Team:** 3 people · **Time:** 6 hours · **Target:** Polished Tier 1

> This document supersedes `plan.md` and `WORKPLAN.md`. It is the single source of truth
> for strategy, tech stack, agreed interfaces, and individual work assignments.

---

## Strategic goal

**One beautiful, complete Tier 1 output.** The rubric says it explicitly: *"a polished
Tier 1 beats a broken Tier 3."* 60% of the score is Editability (30%) + Structural Logic
(35%) + House Style (20%) + Intake (15%) — none of which require multi-level tracks.

Do not scope-creep into Tier 2 or 3. Finish every checklist item below before adding anything new.

---

## The make-or-break technical decision

Most teams lose on **House Style** and **Editability** because they recreate slides with
python-pptx and the result is ugly and off-brand.

**The right approach:** open `master/maverx_master.pptx` as a template and inject text
into its existing slide layouts. `python-pptx` can `add_slide(slide_layout)` from the
master's layout list and fill its placeholders. This gives us:

- House style for free — fonts, colors, and logo live in the master
- Editable text guaranteed — we fill real placeholders, not drawn boxes
- Clean PowerPoint open — no repair prompts

This is the single most important architectural decision. Everything else follows from it.

---

## Tech stack (locked — do not change without a team sync)

| Layer | Library / Tool | Owner | Notes |
|-------|----------------|-------|-------|
| Language | **Python 3.12** | All | Only language in use |
| Deck assembly | **python-pptx** | A | Injects into master layouts |
| Pre/post docs | **python-docx** | A | Editable `.docx` output |
| LLM API | **OpenRouter** via `openai` SDK | B | OpenAI-compatible base URL |
| UI | **Streamlit** | C | Chat + download buttons |
| Schema validation | **jsonschema** | B | Validates LLM output before assembly |
| Config | **python-dotenv** | C | `.env` → `OPENROUTER_API_KEY` |
| Container | **Docker + docker-compose** | C | `docker compose up` = full app |

### Full `requirements.txt`

```
streamlit
python-pptx
python-docx
openai
python-dotenv
jsonschema
```

Pin versions before final commit (`pip freeze > requirements.txt`).

### What we are NOT using

The following were considered and rejected for this hackathon scope:

| Rejected | Why |
|----------|-----|
| FastAPI + React | Two apps to integrate in hour 3–4; Streamlit is enough |
| LangChain / CrewAI | Integration overhead; no value over direct OpenRouter calls |
| Pydantic schemas | JSON Schema file is simpler and shareable without Python imports |
| Google Slides API | Auth complexity; doesn't produce desktop-editable `.pptx` |
| LibreOffice / Marp / Slidev | Don't produce real editable `.pptx` — fails editability rubric |
| LLM writing raw PPTX XML | Produces corrupt decks and repair prompts |

---

## Repo layout

Create this structure at kickoff. Everyone works inside their own folder.

```
/
  master/                     # drop provided assets here first
    maverx_master.pptx
    style_guide.pdf
    example_training.docx
  schema/
    training_spec.schema.json # JSON Schema contract — B emits, A consumes
    sample_spec.json          # hand-written mock — the shared fixture for all three
    layouts.json              # A produces this; B and C depend on it
  engine/                     # Person A owns this folder
    layouts_report.py
    build_pptx.py
    build_docs.py
  content/                    # Person B owns this folder
    intake.py
    generate.py
    prompts/
      intake_system.md
      generate_system.md
  app/                        # Person C owns this folder
    app.py
  output/                     # gitignored; generated files land here
  Dockerfile
  docker-compose.yml
  .env.example
  requirements.txt
  README.md
```

---

## ⚠ BEFORE YOU SPLIT — Agreements required at kickoff (0:00–0:30)

**Do not start isolated work until every item in this section is resolved and committed.**
These are the decisions that prevent merge conflicts, wasted work, and integration failures.

### 1. Assets confirmed in `master/`

All three people verify the following files are present and openable before writing a line of code:
- `master/maverx_master.pptx` — open in PowerPoint and confirm it loads with no errors
- `master/style_guide.pdf` — open and skim fonts, colors, logo rules
- `master/example_training.docx` — read to internalize the kickoff → theory → example → exercise → wrap-up structure

### 2. Layout names confirmed (A does this live, others watch)

A runs `layouts_report.py` on the master and the group agrees on the mapping:

```
kickoff  → <layout name from master>
theory   → <layout name from master>
example  → <layout name from master>
exercise → <layout name from master>
wrapup   → <layout name from master>
```

Write these into `schema/layouts.json` as `block_to_layout` before splitting.
B cannot target layouts without this. A cannot build without confirming which
placeholder indices exist. **This is the most common cause of integration failure.**

### 3. JSON schema frozen

Agree on `schema/training_spec.schema.json` — the exact shape of the JSON that B emits
and A consumes. No field can be added or renamed after this point without a team sync.

```json
{
  "meta": {
    "topic": "", "audience": "", "level": "", "duration": "", "objective": ""
  },
  "slides": [
    {
      "layout": "TitleAndBody",
      "block": "kickoff|theory|example|exercise|wrapup",
      "title": "",
      "bullets": ["", ""],
      "table": { "headers": ["",""], "rows": [["",""]] },
      "notes": {
        "aim": "", "time": "", "instructions": "", "reflective_q": "", "debrief": ""
      }
    }
  ],
  "prebite": "markdown string",
  "postbite": "markdown string"
}
```

Rule: `table` is either a valid table object or `null` — never omitted. `bullets` is
always an array — never `null`. Agree on this explicitly.

### 4. Function signatures frozen

These are the only four boundaries between the three silos. Stub them out in each file,
commit, and do not break them without telling the others.

```python
# content/intake.py  (Person B)
def assess_intake(state: dict) -> dict:
    """
    Given current state dict (may be empty), returns:
      { "status": "question", "text": "...", "field": "audience" }
      { "status": "ready",    "meta": { topic, audience, level, duration, objective } }
      { "status": "refuse",   "text": "...", "missing": ["field", ...] }
    B owns the logic. C owns the UI loop that calls this repeatedly.
    """

# content/generate.py  (Person B)
def generate_spec(meta: dict) -> dict:
    """LLM call(s). Returns full training spec matching training_spec.schema.json.
    Only uses layout names from schema/layouts.json block_to_layout.
    Raises GenerateError on unrecoverable failure."""

# engine/build_pptx.py  (Person A)
def build_pptx(spec: dict, master_path: str, out_path: str) -> str:
    """Consumes spec, fills master layouts, writes speaker notes, returns out_path.
    Raises AssemblyError on bad layout name or malformed spec."""

# engine/build_docs.py  (Person A)
def build_bites(spec: dict, out_dir: str) -> tuple[str, str]:
    """Writes pre-bite and post-bite as .docx files.
    Returns (prebite_path, postbite_path)."""
```

> **Note on `assess_intake` vs `run_intake`:** The previous WORKPLAN had `run_intake()`
> as an interactive blocking call. That fights Streamlit's rerun model. `assess_intake(state)`
> is stateless and callable per message — C holds state in `st.session_state`.

### 5. Sample spec hand-written and committed

Before splitting, the group hand-writes `schema/sample_spec.json` — a realistic ~5 slide
example covering at least kickoff, one theory slide, one exercise slide, and wrapup.
All 5 note fields must be filled. At least one slide has a `table`.

This is the shared fixture. A builds against it. C tests against it. B targets this shape.

### 6. Docker hello-world confirmed

C creates `Dockerfile` + `docker-compose.yml` and confirms `docker compose up` serves a
"Hello Maverx" Streamlit page before the group splits. This proves the container works
before any real code exists, and prevents a broken Docker reveal at hour 5.

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8501:8501"]
    env_file: .env
    volumes:
      - ./master:/app/master:ro
      - ./output:/app/output
```

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.address", "0.0.0.0", "--server.headless", "true"]
```

### 7. OpenRouter API key confirmed

Everyone confirms the key is in `.env` as `OPENROUTER_API_KEY=...` and B can make one
test call before splitting. If the key doesn't work, solve it now — not at hour 3.

### 8. Demo topic chosen

Pick the demo topic now so nobody accidentally tests on it and exhausts its freshness:

> *"3-hour Prompt Engineering training for a Marketing team with no prior AI experience,
> objective: write effective prompts for campaign copy."*

Do not run a full generation on this topic until the hour-4 QA pass.

---

## Silo work assignments

After the kickoff agreements above are signed off and committed, the three people split
and do not need to talk until hour 3 integration.

---

### Person A — PPTX Engine

**Rubric ownership:** Editability (30%) + House Style (20%) = 50% of challenge score.

You work entirely from `schema/sample_spec.json`. You never need B's or C's code to run.

**Your dependency on others:** only the frozen schema and `sample_spec.json` from kickoff.

**What you give others:**
- `schema/layouts.json` with `block_to_layout` — deliver by hour 1 or B is guessing
- Working `build_pptx()` and `build_bites()` signatures — C calls them at hour 3

#### Tasks (in order)

**A1 — Layout report (first, ~30 min, do during kickoff):**
`engine/layouts_report.py` — load the master `.pptx`, iterate all layouts, print each
layout name + index + placeholder `idx`, `type`, and `name`. Write to `schema/layouts.json`.

**A2 — Layout map:**
Decide which master layout serves each didactic block. Add as `block_to_layout` to
`schema/layouts.json`. Confirm with B before splitting.

**A3 — Assembler** `engine/build_pptx.py`:
- `add_slide(layout)` using layout names from `block_to_layout`
- Fill title placeholder + body placeholder by index
- If `table` is not `null`, insert a real `shape.table` — never an image
- Write 5 note fields into `slide.notes_slide.notes_text_frame`, each clearly labeled:
  `Aim:` / `Time:` / `Instructions:` / `Reflective question:` / `Debrief:`
- CLI: `python engine/build_pptx.py schema/sample_spec.json output/test.pptx`
- **Open `output/test.pptx` in real desktop PowerPoint before hour 3** — non-negotiable

**A4 — Docs** `engine/build_docs.py`:
`build_bites(spec, out_dir)` — write `prebite.docx` and `postbite.docx` via python-docx
from the `prebite` and `postbite` fields in the spec.

**A5 — Edge cases:**
Overflowing bullets, missing placeholder index, empty table, special characters, `null`
table field. The deck must open with no repair prompt in desktop PowerPoint.

#### Do NOT
- Touch Streamlit, Docker, prompts, or LLM code
- Draw shapes or text boxes — only fill master placeholders
- Change `schemas.py` or the JSON contract without a team sync

---

### Person B — Content Pipeline

**Rubric ownership:** Structural Logic (35%) + Intake Quality (15%) = 50% of challenge score.

You build against the frozen schema and `schema/layouts.json`. You never need C's Streamlit
code to test. Run CLI: `python content/generate.py --intake schema/sample_intake.json`.

**Your dependency on others:** `schema/layouts.json` (block_to_layout) from A — needed within
hour 1 so your prompt uses real layout names.

**What you give others:**
- `assess_intake()` and `generate_spec()` — C calls both from `app.py`
- A real generated `spec.json` by hour 3 so A can test on genuine content

#### Tasks (in order)

**B1 — Intake logic** `content/intake.py`:

Implement `assess_intake(state: dict) -> dict`. The five required fields:

| Field | Vague-answer examples that need follow-up |
|-------|------------------------------------------|
| `topic` | "something AI-related" → ask for specific skill |
| `audience` | "our team", "everyone" → ask role/department |
| `level` | none given → ask beginner/intermediate/advanced |
| `duration` | "a few hours", "half a day" → ask for minutes |
| `objective` | "learn stuff" → ask what participants should be able to do |

Return `status: "refuse"` with a list of missing fields if incomplete. Never guess silently.

**B2 — Outline generator (LLM call 1):**
From `meta`, derive slide count from duration (~4 min/slide), lay out the arc
**kickoff → theory → example → exercise → wrap-up**, and distribute timing per block so
it sums to the stated duration. Emit a slide-by-slide plan (title + block + time).

**B3 — Content generator (LLM call 2):**
From the outline, fill each slide's `title`, `bullets`, optional `table`, and all 5
note fields. Output must be valid JSON matching the schema. Only use `layout` values
from `schema/layouts.json`.

**B4 — Pre-bite + post-bite:**
Generate `prebite` and `postbite` markdown strings as part of the spec. Pre-bite = article/
install step/reflection prompt before the session. Post-bite = assignment/reflection/reading
after. Both go into the spec JSON (A's assembler and C's download both use them).

**B5 — Robustness:**
Validate LLM output against `schema/training_spec.schema.json` using `jsonschema`.
On failure: retry once with "your JSON had these errors, fix them: ...". Log the raw
response. Raise `GenerateError` only after retry also fails.

#### Prompt discipline

Store prompts in `content/prompts/` as `.md` files — not inline strings.
The generate prompt must explicitly instruct the model:
- Follow kickoff → theory → example → exercise → wrap-up — no exceptions
- Use only layout names from this list: `{block_to_layout values}`
- Every slide must have all 5 note fields
- Timing across all slides must sum to `{duration}` minutes
- Return only valid JSON — no prose, no markdown fences

#### Do NOT
- Touch `build_pptx.py`, Docker, or `app.py`
- Invent layout names — use only what's in `layouts.json`
- One-shot generate + assemble in one call — two separate LLM calls is more robust

---

### Person C — Glue, UX, Docs & QA (Milan)

**Rubric ownership:** UX (8) + Docs (6) + Polish (5) + Setup & Onboarding (4) + Reproducibility (4)
+ Deployment Readiness (3) = **30 execution points**. These are largely "free" points that
teams routinely leave on the table.

> **Status update:** No changes to the function signatures — `assess_intake()` and
> `generate_spec()` are unchanged. `layouts.json` is now filled so the app won't crash on
> missing layouts. The `.env.example` has a new `OPENROUTER_MODEL` var — add it to the
> Docker env docs.

You work against **stubs** of A's and B's functions from minute 30. You are never blocked.

**Your dependency on others:** function signatures (kickoff). Real implementations by hour 3.

**What you give others:**
- Proof the full pipeline works end to end
- Bug list from QA, especially to A on editability issues

#### Tasks (in order)

**C1 — Docker (do by hour 1, before anything else):**

`docker compose up --build` serves a "Hello Maverx" Streamlit page. This is the
first done signal of the day. Use stubs for all functions inside `app.py` until hour 3.

**C2 — Streamlit app** `app/app.py`:

```
Step 1: Chat input → call assess_intake(state) → show question or "ready" summary
Step 2: [Generate Training] button (only visible when status == "ready")
Step 3: Spinner → generate_spec(meta) → build_pptx(...) → build_bites(...)
Step 4: Download buttons for .pptx, prebite.docx, postbite.docx
```

Handle errors: bad LLM JSON → "Generation failed, please try again" (not a crash).
Missing API key → clear message at startup.

Use **stubs** until real functions arrive at hour 3:

```python
def generate_spec(meta):
    import json; return json.load(open("schema/sample_spec.json"))

def build_pptx(spec, master_path, out_path):
    import shutil; shutil.copy("schema/sample_spec.json", out_path); return out_path
```

**C3 — README and docs:**

`README.md` must contain (this is 6 points many teams skip):
1. What the system does (2 sentences)
2. Prerequisites: Docker, API key
3. Setup: `cp .env.example .env` → add key → `docker compose up --build`
4. Usage: open `http://localhost:8501`, fill in the form, download files
5. How to swap the Maverx template: replace `master/maverx_master.pptx` with any
   branded master — the pipeline uses whatever layouts it finds
6. Architecture overview: one paragraph or small diagram

**C4 — House-style verification checklist:**

Read `master/style_guide.pdf` and write a simple checklist. After each generated deck,
verify manually:

- [ ] Fonts match style guide
- [ ] Colors match style guide (title bar, accent, body)
- [ ] Logo present and positioned correctly
- [ ] No blank slides
- [ ] No placeholder text ("Click to add content")

File issues to A with slide number and screenshot.

**C5 — QA in real PowerPoint (hour 4):**

Open the generated deck in **desktop PowerPoint** (not LibreOffice — they behave differently).
Check every slide:

- [ ] No repair prompt on open
- [ ] Every title and body is editable text
- [ ] Tables are real tables (click into a cell)
- [ ] Notes pane shows all 5 fields on every slide
- [ ] Fonts/colors intact after open

**C6 — Demo prep (hour 5):**
One end-to-end run on the agreed demo topic. Time it. Write a 2-minute script for judging.

#### Do NOT
- Fix assembly bugs in `build_pptx.py` — file them to A
- Fix prompt issues in `generate.py` — file them to B
- Add features to the UI beyond intake → generate → download

---

## 6-hour timeline

| Time | All | A (PPTX) | B (Content) | C (Glue) |
|------|-----|----------|-------------|----------|
| **0:00–0:30** | Kickoff agreements, assets confirmed, schema frozen, stubs committed | Layout report live | Read example training | Docker scaffold started |
| **0:30–1:00** | Split | `sample_spec.json` + assembler start | `assess_intake` + OpenRouter wire | **`docker compose up` works** |
| **1:00–2:00** | | Placeholders + notes logic | Intake prompt + follow-up logic | Streamlit stub flow + `validate_spec` |
| **2:00–3:00** | | Table slide + CLI test + **open in PP** | Generate prompt + CLI done | README draft |
| **3:00–4:00** | **Integration hour — protect this** | Fix layout issues from real JSON | Prompt tuning on real output | Replace stubs, E2E in Docker |
| **4:00–5:00** | | Visual QA in PowerPoint | Intake edge cases, vague input | README + error handling |
| **5:00–6:00** | Demo prep | Support demo | Support demo | Final README + dry run |

---

## Sync points (only four — no standing meetings)

| When | Duration | What happens |
|------|----------|--------------|
| **0:30** | 30 min | Schema frozen, layout names agreed, stubs committed, Docker hello-world |
| **3:00** | 15 min | A demos deck from `sample_spec.json`; B demos JSON output; C goes live in Docker |
| **4:00** | 10 min | Pick demo topic run; assign who fixes what from QA |
| **5:30** | 10 min | Dry-run demo; rehearse 2-minute judging script |

Between syncs: communicate blockers only. Use a group chat, not a standing conversation.

---

## Fallback plan

| Problem at hour 3 | Fallback |
|-------------------|----------|
| B's JSON is malformed | C hardcodes `sample_spec.json`; demo shows intake + JSON on screen; B fixes during QA hour |
| A's assembler crashes | B+C demo intake → JSON in browser; A catches up by hour 4 |
| Docker broken | C prioritizes Docker; add `streamlit run app/app.py` as backup in README |
| Tables too complex | Drop table slides; bullets only — still passes editability |
| Speaker notes missing fields | A adds a repair pass: iterate slides, fill any missing note key with "(see instructions)" |

---

## Rubric → owner (so nobody polishes the wrong thing)

| Rubric item | Weight | Primary owner |
|-------------|--------|---------------|
| Structural Logic | 35% | **B** |
| Output Editability | 30% | **A** |
| House Style | 20% | **A** |
| Intake Quality | 15% | **B** |
| UX + Docs + Setup + Polish | 30 pts | **C** |

---

## Innovation bonus (two ideas, do not add a third)

1. **Auto timing distribution** — `generate_spec` splits the stated duration across blocks
   and writes per-slide `time` into notes so a trainer can run to the clock.
2. **Template-agnostic** — because we inject into any master, swapping `master/maverx_master.pptx`
   for another brand's file "just works." README calls this out explicitly. Real differentiator.

---

## Pre-submission checklist

Run through this before judging begins:

- [ ] `docker compose up --build` on a clean pull starts without errors
- [ ] API key is in `.env.example` as a placeholder (not the real key)
- [ ] `.pptx` opens in desktop PowerPoint with no repair prompt
- [ ] All content is editable text — no flattened images
- [ ] Maverx master layouts used — not redrawn slides
- [ ] Fonts, colors, logo match style guide
- [ ] Full didactic arc: kickoff → theory → example → exercise → wrap-up
- [ ] Speaker notes on every slide with all 5 fields
- [ ] Pre-bite and post-bite are separate downloadable files
- [ ] Intake asks 5 questions and handles vague input with follow-ups
- [ ] System refuses to generate until intake is complete
- [ ] README has run instructions, API key setup, and how to swap the template
- [ ] `requirements.txt` has pinned versions
