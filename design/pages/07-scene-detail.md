# 07 — Scene Detail (Fact-Check Panel)

**Route:** `/projects/{id}/bible/scenes/{sceneId}`
**Goal:** the core value-delivery screen — a script supervisor reviewing one scene's claims and their sources.

## Layout
- Center: the scene text/synopsis (Fraunces slugline, Inter body), with flagged phrases underlined in signal-red inline (like a proofreader's mark).
- Below/beside each underlined phrase: a **Claim Row** — the claim as extracted, its Verification Stamp, and an expandable citation list.
- Right rail ("wire feed"): the raw citations for whichever claim is currently expanded — title, domain, retrieved timestamp, a one-line excerpt (mono), and a link out to the source. This is where Parallel's search results are shown directly, so the grounding is fully auditable by a human, not just asserted by the model.
- "Re-check this claim" action per claim, in case a user wants to re-run the Research Agent (demonstrates the integration is live, not cached-only, for the demo).

## States
- `VERIFIED` claim: green-outlined stamp, citations shown collapsed by default.
- `FLAGGED` claim: signal-outlined stamp, citations expanded by default (the whole point is to surface these).
- `UNVERIFIED` claim: slate-outlined stamp, explicit copy: "No supporting or contradicting sources found. Confirm manually before production."
