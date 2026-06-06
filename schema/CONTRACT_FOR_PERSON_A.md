# Spec contract — for Person A (PPTX engine)

This is the **exact JSON** `generate_spec()` produces and your `build_pptx()` / `build_bites()`
consume. It's live-verified end to end. A real, full sample is in
**`schema/sample_generated_spec.json`** — build against that file; you don't need to run the
LLM.

## Top-level shape

```json
{
  "meta":     { "topic", "audience", "level", "duration", "objective" },   // all strings
  "slides":   [ <slide>, ... ],          // 8–24 slides
  "prebite":  "markdown string",          // -> prebite.docx
  "postbite": "markdown string"           // -> postbite.docx
}
```

## Each slide

```json
{
  "block":   "kickoff|theory|example|exercise|wrapup",   // didactic arc, in order
  "layout":  "Title Slide",                               // EXACT master layout name to use
  "title":   "string",                                    // -> title placeholder (idx 0)
  "bullets": ["string", ...],                             // -> body placeholder (idx 1); may be []
  "table":   null | { "headers": ["string", ...],
                      "rows":    [["string", ...], ...] },// real pptx table when present
  "notes":   { "aim", "time", "instructions",            // -> slide.notes_slide, all 5 always present
               "reflective_q", "debrief" }                //    (all strings, never empty)
}
```

## Guarantees (so you can rely on them)

- **`layout` is always one of just TWO layouts** (restricted for the time-limited build),
  both with real placeholders — see `schema/layouts.json`. The `block → layout` map:
  | block | layout |
  |-------|--------|
  | kickoff | Title Only |
  | theory | Title and Content |
  | example | Title and Content |
  | exercise | Title and Content |
  | wrapup | Title and Content |
  - `Title and Content`: idx 0 = title, idx 1 = body (bullets or table)
  - `Title Only`: idx 0 = title, **no body placeholder** — kickoff slides won't have
    rendered bullets there (any `bullets` on a Title Only slide can be ignored)
- **All 6 required slide keys are always present.** `bullets` is always a list (maybe empty).
  `table` is always either `null` or a valid object. `notes` always has all 5 fields, all
  non-empty strings.
- **Table cells are always strings** (already coerced) — safe to drop straight into a pptx table.
- The full **didactic arc is always present**: at least one kickoff, theory, example,
  exercise, and wrapup, in order.

## What you need to render

1. For each slide: `add_slide(layout_by_name[slide["layout"]])`, fill title (placeholder idx 0)
   and body bullets (idx 1). For `Two Content`, idx 1 + idx 2 are the two columns.
2. If `slide["table"]` is not null, insert a real `shape.table` from `headers` + `rows`.
3. Write the 5 notes fields into `slide.notes_slide.notes_text_frame`, labeled
   (Aim / Time / Instructions / Reflective question / Debrief).
4. `prebite` and `postbite` markdown strings → two `.docx` files via python-docx.

Master file: **`master/Maverx - Presentation Style Guide for Hackaton.pptx`**
(a `master/maverx_master.pptx` symlink also points to it).
⚠️ The `Titeldia` / `Aangepaste indeling` layouts have **no placeholders** — use the 6
standard layouts above, which do.
