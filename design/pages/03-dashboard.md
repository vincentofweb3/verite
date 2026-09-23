# 03 — Dashboard (Project List)

**Route:** `/dashboard`
**Goal:** see all script projects and their status at a glance; start a new one.

## Layout
- Left rail: film-can-label navigation (workspace name at top, then a flat list isn't needed here since this *is* the top level — rail shows workspace switcher + Settings link + "New Project" button pinned).
- Center: grid of **Project Cards**, styled like labeled film canisters — title (Fraunces), page count, status chip (`Processing` / `Story Bible Ready` / `Flags Found: N`), last-updated timestamp (mono).
- Empty state (no projects yet): centered message, plain and direct — "No scripts yet. Upload one to build its Story Bible." — with the New Project CTA. No stock illustration; use the stamp motif quietly, unstamped/greyed, as a visual anchor.

## States
- A project card whose Continuity & Rights pass found flagged issues shows a small signal-red count badge ("3 flags") so risk is visible without opening the project.
- Loading: skeleton cards matching the film-canister shape, not generic grey boxes.
