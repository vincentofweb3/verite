# 08 — Continuity Flags

**Route:** `/projects/{id}/continuity`
**Goal:** cross-scene issues in one triage list — the Continuity Agent's output.

## Layout
- A single ranked list (highest production risk first), each row: issue description in plain language ("Silver lighter appears in scene 12, referenced again in scene 40 with no scene establishing its loss or return"), the scenes involved (linked chips → jump to Scene Detail), and a severity tag (mono: `HIGH` / `MED` / `LOW`).
- No chart needed here — this is inherently a list, and treating it as one is the honest layout.
- Each row can be marked "Acknowledged" (script supervisor has seen it, doesn't need to re-surface) — a light checkbox-style state, not a full workflow system.

## States
- Empty state (no flags found): "No continuity issues detected across 42 scenes." — plainly stated, genuinely good news, no celebratory animation (would undercut the tool's authoritative tone).
