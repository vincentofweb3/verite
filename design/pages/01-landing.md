# 01 — Landing Page

**Route:** `/`
**Goal:** in one screen, a filmmaker or script supervisor understands what Vérité does and starts a project.

## Layout
- Full-bleed `ink` background. Hero headline in Fraunces, large: **"Ground every scene in truth."** Subhead in Inter: one sentence naming the real cost ("Continuity errors and unverified facts cause reshoots. Vérité catches them before the camera rolls.")
- Hero visual: an animated example claim resolving live — a scene line typing in, then a Verification Stamp thudding into place with its citation appearing in the wire-feed style. This *is* the product, shown, not described.
- Primary CTA: "Start a project" (signal-red button) → `/signup`. Secondary: "See how it works" → scrolls to the process section.
- Process section: three labeled stages (not a generic numbered list — these are genuinely sequential): **Parse → Ground → Flag**, each with a one-line description and a small mono-styled example (a real claim, a real stamp).
- Social proof / impact section: a short, honestly-worded stat framing the reshoot-cost problem (cite a source if used in the real build; otherwise state it as the framing thesis rather than an invented number).
- Footer: track/hackathon attribution line for judges, link to the public repo.

## States
- No auth required to view. CTA routes to signup if not logged in, to `/dashboard` if already logged in.
