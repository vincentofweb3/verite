# AGENT_BRIEF.md — Operating Instructions for the Building Agents

This file is addressed directly to whichever coding agent (Codex / Claude Opus / other) picks up this repo to implement Vérité.

## Your role
You are writing the code for a hackathon submission. You are a *tool used to build* the product — you are not, yourself, part of the shipped product's runtime. Do not import or call yourself (or any non-Google model API) from within `agents/`, `backend/`, or `frontend/`. See `docs/AUDIT.md` §1–2 for exactly why, and run the CI grep in `docs/IMPLEMENTATION.md` §4 locally before every commit.

## Order of operations
1. Read `docs/AUDIT.md` fully.
2. Read `docs/ARCHITECTURE.md` fully.
3. Follow `docs/IMPLEMENTATION.md` milestone-by-milestone — don't reorder or skip M4 (the Parallel grounding step); it's the track-defining feature.
4. Build each page against its spec in `design/pages/`, using the tokens in `design/DESIGN_SYSTEM.md`. Don't invent a different visual system.

## Non-negotiables
- Every claim shown to the user as "verified" must trace back to an actual Parallel search result stored with it (title, url, snippet). Never fabricate a citation or synthesize one from the model's own knowledge — that defeats the entire premise of the product and would be caught immediately in a live demo.
- Keep `backend/services/gemini_client.py` and `agents/research_agent.py` clean and readable — assume a judge will open exactly these two files first.
- Prefer boring, working infrastructure over clever infrastructure. Cloud Run + Firestore is enough; don't add extra managed services under time pressure.
- If a screenplay upload is empty/malformed, or the Parallel API returns no sources for a claim, the UI must say so plainly ("No sources found — treat as unverified") rather than hide the failure. See `design/DESIGN_SYSTEM.md` voice guidelines on empty/error states.

## When something in this plan doesn't fit reality
The architecture and milestones here are a strong default, not gospel. If the ADK, the Parallel SDK, or Cloud Run behaves differently than described once you're actually building, adapt the implementation — just keep the two hard constraints intact:
1. Reasoning/generation in the shipped app comes from Google Cloud AI only.
2. The Parallel Search API is genuinely called, at runtime, in a real code path, to ground claims with real citations.

## Definition of done for the hackathon submission
- [ ] Deployed, working URL (Cloud Run/Firebase).
- [ ] Public repo with license visible in the About section.
- [ ] `agents/research_agent.py` makes a real Parallel call; `backend/services/gemini_client.py` makes a real Gemini call.
- [ ] All 11 pages in `design/pages/` implemented (a rough but functional pass is fine for lower-priority pages — Dashboard, Script Processing, and Scene Detail are the three that must be polished).
- [ ] 3-minute demo video recorded, uploaded publicly, English.
- [ ] Devpost submission form completed against `docs/SUBMISSION_CHECKLIST.md`.
