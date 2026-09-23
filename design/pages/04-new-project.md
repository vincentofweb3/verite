# 04 — New Project / Script Upload

**Route:** `/projects/new`
**Goal:** get a screenplay into the system with minimal ceremony.

## Layout
- Centered single-column form on `ink` background.
- Project title field.
- Upload dropzone (accepts PDF / Fountain / .txt), styled as a "slot a reel into the can" metaphor via a simple bordered drop target — no cartoon icon, just clear typographic instruction: "Drop a screenplay, or browse."
- Once a file is attached: filename, page count estimate, a "Start processing" primary button.
- A small note under the dropzone in Inter, secondary color: what happens next in one sentence ("Vérité will parse your script into scenes, then research every factual claim it finds.")

## States
- Unsupported file type: plain inline error naming the accepted formats.
- Upload in progress: mono-styled progress readout (bytes / percentage), not a generic spinner — reinforces the "data" feel.
- On success: auto-routes to Script Processing (05).
