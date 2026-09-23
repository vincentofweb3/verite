# DESIGN_SYSTEM.md — Vérité

## Design brief in one sentence
A night editing bay, not a SaaS dashboard: Vérité should feel like the desk of a script supervisor cross-referencing a continuity binder under a lightbox lamp — precise, inky, a little analog, with the red of a tally lamp doing all the emotional work.

## Why not the defaults
Rejected on purpose: warm cream + terracotta serif (too soft for a *fact-checking* tool — this product's whole job is scrutiny, not comfort), near-black + acid-green (too generic-tech, undercuts the "film production" world), broadsheet hairline-rule columns (close, but too journalistic-neutral — we want something with more physical, tactile "desk" feeling: stamps, tabs, film-can labels).

## Color

| Token            | Hex       | Use                                                             |
|-------------------|-----------|------------------------------------------------------------------|
| `ink`             | `#12151B` | App background — near-black with a cool blue undertone, not pure black |
| `paper`           | `#EDE7D9` | Primary text on dark surfaces; card backgrounds in "light mode" panels (report exports) |
| `signal`          | `#C1272D` | The verification stamp, flags, primary CTA — used deliberately, never as decoration |
| `brass`           | `#B08D57` | Secondary accents: dividers, active tab underline, film-reel motifs |
| `slate`           | `#3C4551` | Borders, secondary text, inactive states |
| `verified-green`  | `#4F7942` | "Supported" verdict only — the one place green appears |

Signal red is reserved *only* for verification/flag states and the primary action button — if it starts appearing decoratively, that's a sign to remove it.

## Typography

- **Display — Fraunces** (high optical-size range, bold, slightly irregular serif): used for page titles and the scene sluglines, evoking a film title card. Set large, tight leading, occasional italic for emphasis on report headlines.
- **Body — Inter**: everything a user reads to do their job — scene text, descriptions, form labels. Neutral so it never competes with Fraunces or the citation data.
- **Utility / data — JetBrains Mono**: timestamps, source URLs, confidence scores, the "agent trace" log, and anything that reads like a wire-service feed of citations. This is what makes the citations panel feel like verified, sourced data rather than generated prose.

## Layout concept

Three-zone frame, present (in varying proportions) across the app:

```
┌───────────┬─────────────────────────────────────┬──────────────┐
│  FILM CAN │                                       │   WIRE FEED  │
│   RAIL    │            LIGHTBOX / CONTENT         │   (citations,│
│  (nav,    │        scene cards laid out like       │   agent      │
│  labeled  │        frames on a filmstrip)          │   trace,     │
│  like     │                                       │   sources)   │
│  reel tins)│                                       │              │
└───────────┴─────────────────────────────────────┴──────────────┘
```

- **Left rail:** navigation styled as stacked film-can labels (project name, Story Bible, Continuity, Rights, Settings) — brass rule under the active label.
- **Center:** the primary working surface — changes per page (script list, scene cards, report view).
- **Right rail** (present on Scene Detail, Fact-Check, and Agent Trace views only): a monospace "wire feed" of live citations/sources as they're retrieved, reinforcing that every claim is backed by a real, timestamped source.

## Signature element — the Verification Stamp

A rotated (−4°), rubber-stamp-style badge applied to every checked claim:

```
 ╭──────────────╮
 │  ✓ VERIFIED   │   (signal-red outline + text on transparent,
 ╰──────────────╯    like ink stamped onto paper)
```

Three variants: `VERIFIED` (verified-green outline), `FLAGGED` (signal outline, used for continuity/rights issues), `UNVERIFIED` (slate outline, no sources found — see voice note below). This is the one recurring motif that should make every screenshot instantly recognizable as Vérité.

## Motion
Minimal and purposeful: the agent-trace log types itself in (mimics a teletype, reinforces the "wire feed" concept), and a stamp "thuds" into place (quick scale 1.15→1.0, ~150ms) when a claim's verdict resolves. No ambient background animation, no decorative hover parallax — the tool should feel authoritative, not playful.

## Voice
- Plain, declarative, procedural — like a script supervisor's notes, not marketing copy.
- Errors and empty states describe exactly what happened and what to do next. Example: instead of "Oops! Something went wrong," use "No sources found for this claim. Treat it as unverified until confirmed manually."
- Never invent confidence the system doesn't have — if a claim is unverifiable, the UI says so plainly rather than softening it.

## Components (reused across pages)
- **Scene card:** slugline (Fraunces, small caps), one-line synopsis, chips for characters/props/locations, stamp badge if it has a resolved claim.
- **Claim row:** claim text, verdict stamp, expandable citation list (mono, wire-feed style: title · domain · retrieved timestamp).
- **Agent trace item:** timestamp, agent name, one-line status ("Research Agent → querying Parallel Search for 3 claims in Scene 14").
- **Primary button:** signal-red fill, paper text, small caps, used for exactly one primary action per screen.
