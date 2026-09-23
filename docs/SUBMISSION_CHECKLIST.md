# SUBMISSION_CHECKLIST.md

Use this right before hitting submit on Devpost.

## Devpost form fields
- [ ] **Project title:** Vérité — Ground Every Scene in Truth
- [ ] **Tagline (one line):** An agentic fact-checker for filmmakers — Gemini + Parallel Search catch continuity errors and clearance risks before they cost a reshoot.
- [ ] **Track selected:** Parallel
- [ ] **Hosted project URL:** (Cloud Run / Firebase Hosting URL — test it in an incognito window right before submitting)
- [ ] **Repo URL:** (public GitHub, license visible in About section)
- [ ] **Demo video URL:** (YouTube/Vimeo, public, ≤3 min, English)
- [ ] **Description fields:**
  - Features & functionality → pull from `docs/ARCHITECTURE.md` §2 (the five agents)
  - Technologies used → pull from `docs/ARCHITECTURE.md` §4 (tech stack table)
  - Other data sources → sample screenplays used for the demo (`sample_scripts/`), note their licensing status
  - Findings/learnings → write this honestly once the build is done; judges read for genuine reflection, not marketing copy

## Team
- [ ] All team members (max 4) added as Devpost project members
- [ ] Representative designated if entering as a team

## Final smoke test (do this the day before the deadline, not the day of)
- [ ] Fresh incognito browser: sign up, upload a sample script, watch the agent trace run, open a scene, confirm a Parallel-sourced citation renders correctly, view the Continuity Flags page, export a report.
- [ ] Confirm the CI compliance gate (`docs/IMPLEMENTATION.md` §4) is green on the latest commit.
- [ ] Re-read `docs/AUDIT.md` top to bottom one more time.
