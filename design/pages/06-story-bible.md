# 06 — Story Bible (Overview)

**Route:** `/projects/{id}/bible`
**Goal:** the structured breakdown of the whole script — the primary reference document a script supervisor would live in.

## Layout
- Left rail: tabs for Scenes / Characters / Locations / Props (film-can labels, brass underline on active).
- Center, default "Scenes" tab: scene cards laid out like frames on a filmstrip (a horizontally-scrollable strip per act, or a simple ordered grid for shorter scripts) — slugline, one-line synopsis, chips, and a small stamp icon summarizing that scene's worst verdict (a scene with any `FLAGGED` claim shows the flagged stamp, even if other claims in it are verified).
- Clicking a scene card → 07 (Scene Detail).
- Top of page: aggregate counts — total scenes, total claims checked, verified/flagged/unverified breakdown — as plain mono stats, not a decorative dashboard chart (a chart is only justified if it shows something a number can't; here the numbers *are* the point).

## States
- Filter/search bar to jump to a specific scene or character.
- Empty tabs (e.g., no props extracted) state this plainly rather than showing a blank panel.
