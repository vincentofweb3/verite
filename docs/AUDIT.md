# AUDIT.md — Compliance Checklist Against the Official Rules

Read this before writing code. Stage One judging is pass/fail against these exact points, partly via automated tooling — small mistakes here disqualify an otherwise excellent build.

## 1. AI usage limitation (the one most likely to trip up this team)

> "Projects may only use Google Cloud artificial intelligence tools... No other AI models, agent frameworks, or AI APIs are permitted, regardless of vendor — this includes but is not limited to AWS, Microsoft, OpenAI, and Anthropic AI tools."

**What this means concretely for us:**
- Codex (gpt-5.6-sol) and Claude Opus 5 are fine to use as *your own coding assistants* — the same way a developer uses an IDE or autocomplete. Nothing in the rules restricts what tool wrote the code.
- What is **not allowed** is the *shipped application* calling an OpenAI or Anthropic (or any non-Google) model or API at runtime. That means:
  - ❌ No `openai` SDK, no `anthropic` SDK, no calls to `api.openai.com` or `api.anthropic.com` anywhere in `app/`, `backend/`, or `agents/`.
  - ❌ No LangChain/LlamaIndex chains configured to hit a non-Google model.
  - ✅ Reasoning/generation in the product must come from Gemini via `google-adk`, `google-genai`, `google-generativeai`, or `google-cloud-aiplatform`.
  - ✅ Parallel's Search API (a search/retrieval API, not an LLM) is explicitly required and permitted for the Parallel track.
- **Action item:** add a CI grep step (see `IMPLEMENTATION.md`) that fails the build if `openai`, `anthropic`, or `api.anthropic.com` / `api.openai.com` appear anywhere in the shipped source tree.

## 2. Runtime integration must be real, not decorative

> "must demonstrate the use of Google Cloud and the Partner services at runtime in your code — imported and actually called ... not just named in the README."

- Google Cloud: at least one of `google-adk`, `google-genai`, `google-generativeai`, `google-cloud-aiplatform` must be imported **and** actually invoked from a real code path (agent entry point, not a comment).
- Parallel: the `parallel-web` SDK (Python or TS) — or an equivalent supported integration (Vercel AI SDK `@parallel-web/ai-sdk-tools`, LangChain `ParallelWebSearchTool`, or a Grounding config using Parallel Web Search) — must be imported and called from the Research Agent's actual code path, not just referenced in docs.
- **Action item:** `docs/IMPLEMENTATION.md` names the exact files where each integration lives so there's a single source of truth to point judges to.

## 3. Repository requirements

- [ ] Repo is **public** on GitHub/GitLab/Bitbucket.
- [ ] Repo contains **all** source, assets, and run instructions (no missing submodules, no "ask us for the .env").
- [ ] Open-source license file present **and visible in the repo's About section** (top of repo page) — use MIT or Apache-2.0, add via GitHub's "Add license" UI so it's detected, don't just drop a LICENSE.txt.
- [ ] `README.md` in the shipped repo (separate from this planning repo) includes: setup steps, environment variables needed, and how to run locally + how it's deployed.

## 4. Submission package (Devpost form)

- [ ] URL to the hosted, working project (must actually run — Stage One checks this).
- [ ] Text description: features, tech stack, data sources, findings/learnings.
- [ ] Repo URL (see #3).
- [ ] Track selected: **Parallel**.
- [ ] Demo video, see #5.

## 5. Demo video rules

- [ ] ≤ 3 minutes (only the first 3 minutes are judged if longer).
- [ ] Shows the **actual product functioning**, not a cinematic trailer — despite the hackathon's own "3-Minute Trailer" framing, the rules are explicit: functioning demo, not marketing footage.
- [ ] Uploaded to YouTube or Vimeo, set to **public**.
- [ ] English audio or English subtitles.
- [ ] No third-party logos/trademarks/music that isn't cleared, no third-party ad content, nothing that could read as another company's endorsement.
- [ ] Original work only — no stock footage or content owned by others.

## 6. Originality & platform

- [ ] Project must be **newly created during the Contest Period** (July 27 – Sep 9, 2026) — don't reuse a pre-existing repo.
- [ ] Must run on web, Android, or iOS. We are targeting **web**.
- [ ] Any third-party SDK/data used must be properly licensed for this use (e.g., don't scrape a screenplay database without rights — use user-uploaded scripts or clearly-licensed public-domain scripts for the demo).

## 7. Team & eligibility

- [ ] Max 4 individuals per team, all added as Devpost project members.
- [ ] One person designated as Representative if entering as a team/org.
- [ ] Confirm no team member resides in an excluded country (see rules §4) and isn't a Google/Devpost/Partner employee or immediate family thereof.

## 8. Judging criteria to keep visible while building

Equal-weighted in Stage Two — design every feature with these four in mind:
1. **Technological Implementation** — real, working Gemini + Parallel integration, not a mock.
2. **Design** — a coherent product, not a tech demo. This is why the `design/` folder exists.
3. **Potential Impact** — be able to state, with numbers if possible, the cost of the problem we solve (reshoot cost, researcher-hours).
4. **Quality of the Idea** — non-obvious, shows real understanding of a film production workflow, not a generic "search wrapper."

## 9. Key dates

- Contest period: **Jul 27 – Sep 9, 2026, 2:00 PM PT** (hard submission deadline).
- $100 GCP credit request form deadline: **Aug 31, 2026, 11:59 PM PT** — request this immediately, don't wait.
- Judging: **Sep 23 – Oct 7, 2026**.
