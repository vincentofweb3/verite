# 05 — Script Processing (Live Agent Trace)

**Route:** `/projects/{id}/processing`
**Goal:** the single strongest demo moment — show the multi-agent pipeline actually working, in real time.

## Layout
- Center: a vertical **agent trace log**, teletype-in effect, one line per event, mono font:
  ```
  09:14:02  Script Parser Agent      → 42 scenes extracted
  09:14:06  Entity Extraction Agent  → 118 entities, 27 claims flagged
  09:14:09  Research Agent           → querying Parallel Search: "1987 car phone plausibility"
  09:14:11  Research Agent           → 3 sources retrieved, verdict: Contradicted
  09:14:11  Continuity Agent         → prop 'silver lighter' missing after scene 31
  ...
  ```
- Right rail: as claims resolve, their Verification Stamps appear live in a small feed, so the signature motif is visible from the first minute of using the product.
- Progress indicator at top: which of the five agents (Parser → Extraction → Research → Continuity → Synthesis) is currently active, styled as five film-can labels lighting up in sequence — a real sequence, so numbering/order here is earned, not decorative.
- On completion: primary CTA "Open Story Bible" → 06.

## States
- If Parallel returns no sources for a claim, that line reads plainly: "No sources found — marked unverified" (not hidden, not styled as an error, just factual).
- If processing fails outright, the log ends with a clear, specific line naming what failed and a "Retry" action.
