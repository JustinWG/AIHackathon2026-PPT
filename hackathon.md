# AI Hackathon Haarlem — Maverx Challenge

## AI-Powered Training Builder

Build a system that takes a trainer from a one-sentence idea to a complete, editable PowerPoint deck in Maverx house style — in under 10 minutes. Not a content dump. A structured production assistant that follows a fixed didactic model and keeps the human in control of quality.

> Every team participating in this challenge gets 20 EUR of OpenRouter API credits. Contact the team for an API key.

---

## What You Receive

| Item | What It Is |
|------|-----------|
| Style Guide (PDF) | Colors, fonts, logos — the visual rules |
| Master slides (.pptx) | All slide layouts in Maverx house style — use these, don't recreate them |
| Example training (.docx) | A written outline of an existing Maverx training so you understand the structure |

---

## The Intake

Your system must ask at least these 5 questions before generating anything:

| # | Question | Why |
|---|----------|-----|
| 1 | What is the topic or skill to be trained? | Sets the domain |
| 2 | Who is the target audience? | Sets tone and depth |
| 3 | What is the knowledge level of participants? | Beginner / intermediate / advanced |
| 4 | How long is the training? | Determines module count and slide count |
| 5 | What is the primary learning objective? | Anchors the entire structure |

If input is vague, your system should ask follow-up questions — not guess silently. It should refuse to generate until intake is sufficiently complete.

---

## The Didactic Model

Every generated training must follow this structure. No exceptions:

| Block | Purpose |
|-------|---------|
| Kick-off | Set learning goals, introduce agenda |
| Theory | Core concepts, explained for the audience |
| Example | Concrete, recognizable illustration of the theory |
| Exercise | Active application — individual, pair, or group work |
| Wrap-up | Key takeaways, link to practice, next steps |

---

## The Output

- **Format:** .pptx — fully editable in Microsoft PowerPoint
- **Layout:** Based on the provided Maverx master slides (reference them, don't redraw)
- **Content per slide:** Title + body text / bullet points — editable text, not screenshots or images
- **Speaker notes per slide**, containing all 5 fields:
  1. Aim of the slide
  2. Time indication
  3. Instruction steps
  4. A reflective question for learners
  5. A debrief summary
- **Pre-bite:** A short preparation document for participants before the session (article to read, software to install, or reflection question)
- **Post-bite:** A follow-up document after the session (reflection questions, assignment, or further reading)

---

## Challenge Tiers

Pick your ambition level. Scope is rewarded only when matched by quality — a polished Tier 1 beats a broken Tier 3.

### Tier 1 — Single Training

Generate one complete training on a given topic.

> Example: *"Create a 3-hour training on Prompt Engineering for the Marketing team. Participants have no prior AI experience."*

**Required deliverables:**

- Intake via targeted questions
- Generated training structure following the didactic model
- Full editable .pptx in Maverx house style (~20 slides) with text, tables, and visuals — not placeholder screenshots
- Pre-bite and post-bite documents
- Speaker notes on every slide (all 5 fields)

**Bonus:**

- In-session exercises: step-by-step exercise description (tool-based) or case handout with model reference sheet (methodology-based)

### Tier 2 — Multi-Level Module

Generate a 3-level learning track: Essentials, Advanced, Expert. Levels must build on each other — Expert assumes knowledge from the lower levels.

> Example topics: Power BI, Power Automate, Excel, Claude/AI Literacy

**Required deliverables per level:**

- Everything from Tier 1
- Mentimeter recap in sessions 2 and 3 to revisit the previous session

**Bonus:**

- For tool-based trainings: generate adjustable datasets

**Key challenge:** Level 2 must presuppose level 1. Content, exercises, and difficulty must scale logically.

### Tier 3 — Certification Track

Generate a full multi-session certification programme with a coherent narrative thread.

> Example: Lean Black Belt — 8 sessions of 2 hours, structured along DMAIC

**Required deliverables per session:**

- Everything from Tier 1, plus a full case handout (realistic business case + model reference + space to apply)

**Required at track level:**

- Logical structure across all sessions (e.g., DMAIC backbone)
- Consistent fictional case running through the entire track — participants build on their work each session
- Session overview document showing the red thread, timing, and learning objectives per session
- Post-bite of session N connects directly to pre-bite of session N+1

**Key challenge:** Narrative and didactic consistency across 16 hours of training material. (Attention Token Heavy)

---

## What Is Up to You

We do **not** judge on:

- Which AI model(s) or APIs you use
- Whether the interface is a chat, web form, script, or something else
- How the PowerPoint is generated technically

We judge on **results**: what comes out the other end.

---

## Judging Criteria

Your submission is scored out of 100 points across three categories:

| Category | Points | What It Covers |
|----------|--------|----------------|
| Challenge-Specific Criteria | 60 | Does it solve the Maverx challenge well? |
| Overall Execution Quality | 30 | How well is it built, documented, and delivered? |
| Innovation Bonus | 10 | Does it bring breakthrough thinking or creative execution? |

### Challenge-Specific Criteria (60 points)

| Criterion | Points | What Matters |
|-----------|--------|--------------|
| Structural Logic | 21 | Is the didactic arc present? Are exercises matched to theory? Are speaker notes complete? Is timing distributed sensibly? Could a trainer actually teach from this? |
| Output Editability | 18 | Does the .pptx open cleanly in PowerPoint? Is all content editable text/tables? Can titles, bullets, and tables be edited? Does the pipeline handle edge cases? |
| House Style Compliance | 12 | Are Maverx master slides referenced (not recreated)? Are fonts, colors, and logo placement intact? Is layout discipline maintained across all slides? |
| Intake Quality | 9 | Are the 5 required questions asked? Does the system handle vague input with follow-ups? Does it refuse to generate until intake is complete? |

### Overall Execution Quality (30 points)

| Criterion | Points | What Matters |
|-----------|--------|--------------|
| User Experience | 8 | Is the interface intuitive? Does it handle errors gracefully? Can a first-time user accomplish the core task without reading documentation? |
| Documentation | 6 | Can someone understand what it does, how to use it, and how it works without the team present? Clear README, setup guide, and architecture overview? |
| Polish & Attention to Detail | 5 | Does it feel finished? Visual consistency, edge case handling, no obvious bugs? |
| Setup & Onboarding | 4 | How easy is it to get the system running? Are dependencies clear? Does the first-run experience work? |
| Reproducibility & Code Quality | 4 | Can someone else run it, understand the code, and modify it? |
| Deployment Readiness | 3 | How far is this from production? Could Maverx actually deploy this with minimal additional work? |

### Innovation Bonus (10 points)

| Score | Description |
|-------|-------------|
| 0-2 pts | Standard hackathon execution; nothing unexpected |
| 3-5 pts | One genuinely fresh idea that adds value |
| 6-8 pts | Multiple creative contributions; you think "that's clever" |
| 9-10 pts | Breakthrough thinking; you think "why hasn't anyone done this before?" |

Innovation must add value, not just novelty. A creative idea that ignores the challenge requirements scores low.

---

## Deliverables

1. Intake via targeted questions (5 required questions + follow-ups for vague input)
2. Generated training structure following Maverx didactic model (kick-off -> theory -> example -> exercise -> wrap-up)
3. Full editable .pptx in Maverx house style (30-50 slides) with text, tables, and visuals — no placeholder screenshots
4. Speaker notes on every slide (all 5 fields: aim, time, instructions, reflective question, debrief)
5. Pre-bite preparation document for participants
6. Post-bite follow-up document after the session

---

## Quick-Reference Checklist

- [ ] .pptx opens cleanly in desktop PowerPoint — no repair prompts
- [ ] All content is editable text/tables — no flattened images
- [ ] Maverx master slides are referenced, not redrawn
- [ ] Fonts, colors, logo placement match the style guide
- [ ] Full didactic arc present: kick-off -> theory -> example -> exercise -> wrap-up
- [ ] Speaker notes on every slide with all 5 fields
- [ ] Pre-bite and post-bite produced as separate editable files
- [ ] Intake asks the 5 required questions and handles vague input
- [ ] System refuses to generate until intake is complete
- [ ] README with run instructions included
- [ ] Dependencies and API keys documented
- [ ] Path for swapping style guide is documented or self-evident

---

## Provided Assets

| Asset | Description |
|-------|-------------|
| Style Guide (PDF) | Colors, fonts, logos |
| Master slides (.pptx) | All slide layouts in Maverx house style |
| Example training (.docx) | Written outline of an existing Maverx training |

## Tools & Resources

- AI model or API of your choice (OpenAI, Anthropic, local models, etc.)
- PPTX generation library (python-pptx, PptxGenJS, Apache POI, etc.)
- Interface: chat, web form, script, or anything else — your choice

## FAQ

**What is Tier 1 — Single Training?**
Generate one complete training on a given topic. Required: intake via targeted questions, generated training structure following the didactic model, full editable .pptx (30-50 slides), pre-bite and post-bite documents, speaker notes on every slide. Bonus: in-session exercises with step-by-step descriptions or case handouts.

**What is Tier 2 — Multi-Level Module?**
Generate a 3-level learning track: Essentials, Advanced, Expert. Levels must build on each other — Expert assumes knowledge from the lower levels. Required per level: everything from Tier 1 plus Mentimeter recap in sessions 2 and 3. Key challenge: Level 2 must presuppose level 1. Content, exercises, and difficulty must scale logically.

**What is Tier 3 — Certification Track?**
Generate a full multi-session certification programme with a coherent narrative thread. Required per session: everything from Tier 1 plus a full case handout. Required at track level: logical structure across all sessions, consistent fictional case running through the entire track, session overview document, post-bite of session N connects to pre-bite of session N+1. Key challenge: narrative and didactic consistency across 16+ hours of training material.

**Do we have to use a specific AI model?**
No. The choice of AI model(s) or APIs is entirely up to you. We evaluate results, not technical choices.

**What format should the interface be?**
Anything works. Chat, web form, CLI script, or something else — as long as the intake flow and iterative confirmation process are clear.

**What's a pre-bite and post-bite?**
A pre-bite is a short preparation document sent before the session (article, reflection question, software install). A post-bite is a follow-up sent after (reflection questions, further reading, assignment).

**What are the speaker notes?**
Per-slide facilitation guide with 5 fields: Aim of the slide, Time indication, Instruction steps, A reflective question for learners, A debrief summary.
