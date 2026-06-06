# WORKPLAN — Who builds what, and what each person needs

This is the build-level plan. Read `plan.md` first for strategy.
The golden rule: **agree on the interface stubs below in the first 30 minutes, then
everyone builds in parallel against mocks.** Nobody waits on a running version of anyone
else's code.

---

## Repo layout (create this at kickoff)

```
/
  master/                     # provided assets — drop them here first
    maverx_master.pptx
    style_guide.pdf
    example_training.docx
  schema/
    training_spec.schema.json # the contract (B emits, A consumes)
    sample_spec.json          # hand-written mock deck — the shared fixture
    layouts.json              # A produces this from the master (B/C depend on it)
  engine/                     # Person A
    layouts_report.py
    build_pptx.py
    build_docs.py
  content/                    # Person B
    intake.py
    generate.py
    prompts/
  app/                        # Person C
    app.py
  output/                     # generated decks land here
  requirements.txt
  .env                        # OPENROUTER_API_KEY=...
  README.md
```

---

## The shared contract — freeze these at minute 30

These four function signatures are the ONLY thing the three of you share. Stub them out,
commit, and then never break them without telling the others.

```python
# content/intake.py  (Person B)
def run_intake() -> dict:
    """Interactive. Asks the 5 required questions, follow-ups on vague answers,
    refuses to finish until complete. Returns the `meta` dict."""
    # returns: {topic, audience, level, duration, objective}

# content/generate.py  (Person B)
def generate_spec(meta: dict) -> dict:
    """LLM pipeline. meta -> full training spec matching training_spec.schema.json.
    Only uses layout names that exist in schema/layouts.json."""

# engine/build_pptx.py  (Person A)
def build_pptx(spec: dict, master_path: str, out_path: str) -> str:
    """Fills the master's layouts from spec, writes speaker notes, returns out_path."""

# engine/build_docs.py  (Person A)
def build_bites(spec: dict, out_dir: str) -> tuple[str, str]:
    """Writes pre-bite and post-bite as .docx. Returns (prebite_path, postbite_path)."""
```

`app.py` (Person C) is just: `meta = run_intake(); spec = generate_spec(meta);
build_pptx(...); build_bites(...)` + download links.

---

## The training spec schema (the JSON B emits, A consumes)

```json
{
  "meta": { "topic": "", "audience": "", "level": "", "duration": "", "objective": "" },
  "slides": [
    {
      "layout": "TitleAndBody",
      "block": "kickoff|theory|example|exercise|wrapup",
      "title": "",
      "bullets": ["", ""],
      "table": { "headers": ["",""], "rows": [["",""]] },   // or null
      "notes": {
        "aim": "", "time": "", "instructions": "",
        "reflective_q": "", "debrief": ""
      }
    }
  ],
  "prebite": "markdown string",
  "postbite": "markdown string"
}
```

---

# Person A — PPTX Engine (strongest builder)

You own everything that produces files. Most-judged component (Editability 30% + House
Style 20%). You can work entirely from `schema/sample_spec.json` — you never need B's code.

### Tasks
- **A1 (do FIRST, ~30 min — others are blocked on this):** `layouts_report.py`
  Load `master/maverx_master.pptx`. For every slide layout print: name, index, and each
  placeholder's `idx`, `type`, and `name`. Write it to `schema/layouts.json`.
  → This tells B exactly which `layout` strings are legal and what fields fill.
- **A2:** Decide the **layout map** — which master layout serves each didactic block
  (e.g. title layout → kickoff, content layout → theory/example, two-content → exercise,
  closing layout → wrapup). Put it in `schema/layouts.json` as `block_to_layout`.
  Hand this to B.
- **A3:** `build_pptx.py::build_pptx(spec, master_path, out_path)`
  - `add_slide(layout)` from the master for each slide
  - fill title placeholder + body placeholder (handle bullet levels)
  - if `table` present, insert a **real pptx table** (not an image)
  - write the 5 note fields into `slide.notes_slide.notes_text_frame`, each labeled
    (`Aim:`, `Time:`, `Instructions:`, `Reflective question:`, `Debrief:`)
- **A4:** `build_docs.py::build_bites(spec, out_dir)` — pre-bite + post-bite markdown → `.docx`
  via python-docx.
- **A5:** Edge cases — overflowing bullets, missing placeholder index, empty table,
  special characters. The deck must open in desktop PowerPoint with **no repair prompt.**

### What you NEED from others
- The frozen schema + `sample_spec.json` (from kickoff). After that, nothing.

### What you GIVE others
- `schema/layouts.json` (B + C blocked on it) — **deliver within the first hour**
- working `build_pptx` / `build_bites` signatures (C calls them)

---

# Person B — Content Pipeline (prompt engineering)

You own intake + all LLM generation. This is where Structural Logic (35%) and Intake (15%)
are won. You build against `schema/layouts.json` (from A) and the frozen schema.

### Tasks
- **B1:** `intake.py::run_intake()` — collect the 5 required fields:
  topic, audience, knowledge level, duration, learning objective.
  - Validate each for vagueness (e.g. audience "everyone", duration "a while") → ask a
    targeted follow-up instead of guessing.
  - **Refuse to return** until all 5 are sufficiently specific. (Judges test this.)
- **B2:** Outline generator (LLM) — from `meta`, derive module + slide count from the
  duration, lay out the arc **kickoff → theory → example → exercise → wrap-up**, and
  **distribute timing per block** so it sums to the stated duration.
- **B3:** Slide content generator (LLM) — for each planned slide emit title, bullets,
  optional table, and all **5 speaker-note fields**. Output must be valid JSON matching the
  schema and only use `layout` names from `layouts.json`.
- **B4:** Pre-bite + post-bite generation (article/install/reflection before; reflection/
  assignment/reading after).
- **B5:** Robustness — JSON-validate the LLM output and retry/repair on malformed output.
  Cache the API key in `.env` (OpenRouter).

### What you NEED from others
- `schema/layouts.json` + `block_to_layout` from **A** (legal layout names) — first hour
- The frozen schema (kickoff)
- The OpenRouter API key in `.env`

### What you GIVE others
- `run_intake()` and `generate_spec(meta)` — C calls both
- An early **real** `sample_spec.json` once B3 works, so A can test on real content

---

# Person C — Glue, UX, Docs & QA

You own the experience and ~23 "free" execution points (UX 8 + Docs 6 + Polish 5 + Setup 4).
You build against **stubs** of A's and B's functions from minute 30, so you're never blocked.

### Tasks
- **C1:** `app/app.py` — interface (Streamlit chat is fastest, CLI is fine). Flow:
  `run_intake()` → show collected meta → `generate_spec()` → `build_pptx()` +
  `build_bites()` → present download links. Handle errors gracefully (don't crash on a bad
  LLM response — show a friendly message).
- **C2:** `requirements.txt`, `.env.example`, and **README.md**: what it does, setup steps,
  where the API key goes, how to run, and **how to swap the style guide** (drop a new master
  `.pptx` in `master/`). Documentation is 6 points teams routinely skip.
- **C3:** House-style verification — read `style_guide.pdf`, make a checklist (fonts,
  colors, logo placement), and eyeball each generated deck against it.
- **C4:** QA loop — open the deck in **real desktop PowerPoint**: no repair prompt, all text
  editable, table is a real table, all 5 note fields present on every slide. File bugs to A.
- **C5:** Demo prep — one polished end-to-end run + a 2-minute script for judging.

### What you NEED from others
- The four function signatures (kickoff) so you can stub them
- Working `build_pptx`/`build_bites` from A and `run_intake`/`generate_spec` from B by hour 3
- The style guide PDF in `master/`

### What you GIVE others
- The interface that proves the whole pipeline works end to end
- The bug list from QA (esp. to A on editability)

---

## Critical path & sync points

1. **0:00–0:30** — all together: drop assets in `master/`, freeze schema + 4 signatures,
   commit stubs + `sample_spec.json`.
2. **~1:00** — A delivers `layouts.json` → unblocks B's layout targeting.
3. **~3:00** — first real `generate_spec` output feeds A's real `build_pptx`. Integrate.
4. **3:00–4:00** — wire B→A→C in `app.py`. Protect this hour.
5. **4:00–6:00** — QA, house-style pass, README, demo.

**Biggest risks:** (a) layouts.json late → B is guessing; do it first. (b) integration left
to the end → reserve hour 3–4. (c) speaker notes / tables not surviving a PowerPoint open →
C must test in real PowerPoint, not just LibreOffice.
