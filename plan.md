# Maverx AI Training Builder — Hackathon Plan

**Team:** 3 people · **Time:** 6 hours · **Target tier:** Polished Tier 1

---

## The single most important strategic decision

**Target a polished Tier 1, not a broken Tier 2/3.** The rubric says it explicitly:
*"a polished Tier 1 beats a broken Tier 3."* 60% of the score is structural logic +
editability + house style + intake — none of which require multi-level tracks. Nail one
beautiful ~20-slide deck end to end.

## The make-or-break technical insight

Most teams lose on **House Style (20%)** and **Editability (30%)** because they *recreate*
slides with python-pptx and it comes out ugly and off-brand. Don't.

**Open the provided master `.pptx` as the template and inject text into its existing slide
layouts.** python-pptx can `add_slide(slide_layout)` from the master's layouts and fill
placeholders. This gets us:

- House style for free (fonts/colors/logo live in the master)
- Guaranteed editable text (we fill real placeholders, not drawn boxes)
- Clean open in PowerPoint, no repair prompts

First task for one person: open the master in python-pptx and **print every layout name +
its placeholder indices**, so we know exactly what we can fill.

## The contract that stops the team colliding

Spend the **first 30 minutes together** defining one JSON schema — the "training spec" the
LLM produces and the PPTX engine consumes:

```json
{
  "meta": { "topic": "...", "audience": "...", "level": "...", "duration": "...", "objective": "..." },
  "slides": [
    {
      "layout": "TitleAndBody",        // must match a master layout name
      "block": "theory",               // kickoff|theory|example|exercise|wrapup
      "title": "...",
      "bullets": ["...", "..."],
      "table": null,
      "notes": { "aim": "...", "time": "...", "instructions": "...", "reflective_q": "...", "debrief": "..." }
    }
  ],
  "prebite": "...markdown...",
  "postbite": "...markdown..."
}
```

Once frozen, all three work in parallel against it without talking.

## Work division (3 people)

| Person | Owns | Why |
|---|---|---|
| **A — PPTX Engine** | python-pptx code: JSON → fills master layouts → writes speaker notes into `slide.notes_slide` → outputs `.pptx`. Also pre-bite/post-bite as `.docx`. | Hardest, most critical, most "judged." Strongest builder. |
| **B — Content Pipeline** | LLM layer (OpenRouter): intake gate (5 required questions + vague-input follow-ups + refuse-until-complete), then prompt(s) emitting the JSON spec following kickoff→theory→example→exercise→wrap-up with all 5 speaker-note fields and sensible timing. | Where Structural Logic (35%) and Intake (15%) are won. |
| **C — Glue + UX + Docs + QA** | Interface (simple Streamlit/CLI chat: intake → B → A → files), README/setup docs, house-style verification, demo prep. | Documentation, Setup, UX, Polish add up to a lot of "free" execution points. |

**Mock the contract immediately:** A doesn't wait for B. A hand-writes one fake JSON spec
and builds the whole engine against it. B builds the LLM to emit that same shape. They meet
in the middle around hour 3.

## 6-hour timeline

- **0:00–0:30** — All: read style guide + example training, agree on JSON schema, A dumps master layout names.
- **0:30–3:00** — Parallel build against mocks. A: engine produces a perfect deck from hand-written JSON. B: intake + content generation emits valid JSON. C: interface skeleton + README started.
- **3:00–4:00** — **Integration.** Wire B→A→C end to end. Protect this hour — it always runs long.
- **4:00–5:00** — Quality pass: open the deck in real PowerPoint (no repair prompt), verify every slide is editable text, check fonts/colors/logo, confirm all 5 note fields on every slide, generate pre/post-bite.
- **5:00–6:00** — Polish, finalize README (run instructions + API keys + "how to swap the style guide"), practice a 2-min demo.

## Two cheap innovation-bonus ideas (don't overbuild)

- **Auto timing distribution** — system splits the stated duration across blocks and writes per-slide time into speaker notes, so a trainer can run it on the clock. Hits "is timing distributed sensibly."
- **Style-guide-agnostic** — because we inject into *any* master template, swapping Maverx for another brand's `.pptx` "just works." A real "why hasn't anyone done this" deployment story.

## Verify early so we don't get burned

- Speaker notes go in `slide.notes_slide.notes_text_frame` — confirm python-pptx writes them and they survive a PowerPoint open.
- Tables must be real pptx tables, not images.
- The intake must actually **refuse** to generate when incomplete — easy points teams skip.
