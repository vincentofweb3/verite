# 10 — Export & Share

**Route:** `/projects/{id}/export`
**Goal:** get the Story Bible + reports out of the tool and into a production's existing paperwork.

## Layout
- Simple choice screen: export format (PDF "Continuity Binder" styled to echo the app's own visual system — stamps and all; or structured JSON/CSV for pipeline integration), and a scope selector (full Story Bible / Fact-Check Report only / Continuity & Rights only).
- Shareable link option: generates a read-only view for a collaborator who isn't a Vérité account holder, with an expiry.

## States
- Export in progress: mono progress readout, matching the upload page's pattern for consistency.
- Completed: direct download + copyable share link, both visible at once (no forced modal).
