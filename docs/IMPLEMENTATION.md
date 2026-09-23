# IMPLEMENTATION.md — Build Plan

## 0. Before the first commit
- [ ] Create the GCP project, enable Vertex AI API, Firestore, Cloud Run, Cloud Storage.
- [ ] Request the $100 GCP credit (form linked in the Official Rules) — do this on day one, approval takes 1–5 business days.
- [ ] Sign up for Parallel API access and get an API key.
- [ ] Create the public GitHub repo, add an OSS license (MIT) via GitHub's UI so it shows in the About section immediately.
- [ ] Add the CI compliance check from `docs/AUDIT.md` §2 as the very first commit, so it guards every commit after.

## 1. Repo scaffold

```
verite-app/                        ← this is the SHIPPED repo (separate from the planning repo)
├── README.md                      ← setup + run instructions, tech stack, what judges should look at
├── LICENSE                        ← MIT, added via GitHub UI
├── .github/workflows/ci.yml       ← runs the "no disallowed AI vendor" grep + lint + tests
├── agents/
│   ├── orchestrator.py            ← ADK agent graph definition
│   ├── script_parser_agent.py
│   ├── entity_extraction_agent.py
│   ├── research_agent.py          ← ★ imports & calls parallel-web SDK here
│   └── continuity_rights_agent.py
├── backend/
│   ├── main.py                    ← FastAPI app, Cloud Run entrypoint
│   ├── routers/
│   │   ├── projects.py
│   │   ├── scripts.py
│   │   └── reports.py
│   ├── models/                    ← Pydantic schemas mirroring the Firestore data model
│   └── services/
│       ├── gemini_client.py       ← ★ imports & calls google-genai / google-cloud-aiplatform
│       ├── parallel_client.py     ← thin wrapper around parallel-web SDK
│       └── firestore_client.py
├── frontend/                      ← Next.js app, one route per page in design/pages/
│   └── ... (see design/ for per-page specs)
├── infra/
│   ├── cloudrun-backend.yaml
│   ├── cloudrun-frontend.yaml
│   └── firestore.rules
└── sample_scripts/                ← 1–2 public-domain screenplay excerpts for the demo
```

## 2. Milestones

**M1 — Skeleton & auth (day 1–2)**
- Repo scaffold above, empty routes, Firebase Auth wired, deploy an empty "Hello Vérité" to Cloud Run so the deployment pipeline is proven early.

**M2 — Script ingestion + parsing (day 2–3)**
- Upload endpoint → Cloud Storage → Script Parser Agent → scenes written to Firestore.
- Frontend: New Project page + Script Processing (live trace) page.

**M3 — Entity extraction (day 3–4)**
- Entity Extraction Agent running per scene, populating characters/props/locations/claims.
- Frontend: Story Bible overview page.

**M4 — Parallel grounding (day 4–6, the core deliverable)**
- `research_agent.py` calls Parallel Search API for every `needs_grounding` claim.
- Store verdict + sources on the claim.
- Frontend: Scene detail page with the fact-check panel showing citations.
- **This is the piece to over-invest in** — it's the track-defining feature and the strongest demo moment.

**M5 — Continuity & rights pass (day 6–7)**
- Continuity & Rights Agent runs once the full Story Bible exists; produces the Continuity Flags and Rights & Clearance pages.

**M6 — Synthesis, export, polish (day 7–8)**
- Synthesis Agent compiles the final report; PDF/share export.
- Visual polish per `design/DESIGN_SYSTEM.md`.

**M7 — Demo video + submission (day 8–9)**
- Script a 3-minute walkthrough: upload → live agent trace → a caught anachronism with its Parallel citation → a continuity flag → exported report.
- Fill Devpost form, double-check every item in `docs/SUBMISSION_CHECKLIST.md`.

## 2.5 Confirmed from the official Parallel resources page — pick one integration path deliberately

The hackathon's own Parallel resources page (`agentic-cinema.devpost.com/details/parallel-resources`) lays out three valid ways to satisfy the runtime-usage requirement. Choose one and be able to point a judge straight at it — don't blend all three, that reads as unfocused:

1. **Direct SDK call** (what `docs/ARCHITECTURE.md` §2.3 assumes) — `parallel-web` SDK called from `research_agent.py`. Most control over the verdict logic, most code to show off.
2. **Native Gemini grounding** — Gemini Enterprise Agent Platform supports "Grounding with Parallel Search" as a first-class grounding source (see `docs/parallel.ai/integrations/google-gemini-enterprise` and the grounding doc linked from the resources page). This is the *most idiomatic* Google-Cloud-native path and directly matches the hackathon's own framing of "Technical Producer connecting secure data pipelines via managed MCP servers" — worth strong consideration since it demonstrates platform fluency, not just an API call.
3. **Parallel Search & Extract MCP server** — Google Cloud Agent Builder supports managed MCP servers; wiring the Research Agent to Parallel's official MCP server is the closest fit to the hackathon's own "orchestrate the system, don't just write code" framing, and is a strong story for the "Quality of the Idea" judging criterion.

**Recommendation:** prototype with the direct SDK first (fastest to get working end-to-end for M4), then, time permitting, migrate the Research Agent to the MCP-server or native-grounding path for the final submission — it's a better demo narrative ("we orchestrate a managed MCP pipeline," not "we call an API") and scores better against "effectively uses the Partner service," not just "uses" it.

## 3. The two integration points judges will check first

1. `backend/services/gemini_client.py` — real `google-genai`/`google-cloud-aiplatform` call, not a stub.
2. `agents/research_agent.py` — real `parallel-web` SDK call, not a stub. Example shape:

```python
from parallel import Parallel  # official parallel-web SDK

client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])

def ground_claim(claim_text: str) -> GroundingResult:
    result = client.search(
        objective=f"Verify this claim for film production fact-checking: {claim_text}",
        processor="base",
    )
    # feed result.results (title, url, excerpt) into Gemini for the verdict
    ...
```

Keep this file small and readable — it's likely to be the single most-inspected file in the repo.

## 4. CI compliance gate (paste into `.github/workflows/ci.yml`)

```yaml
- name: Disallowed AI vendor check
  run: |
    if grep -RniE "openai|anthropic|api\.openai\.com|api\.anthropic\.com" \
        --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
        agents backend frontend; then
      echo "Disallowed AI vendor reference found in shipped source — see docs/AUDIT.md" && exit 1
    fi
```

## 5. Demo content

Use 1–2 short, clearly public-domain or original screenplay excerpts under `sample_scripts/` (write an original 3–5 page scene, or use a script with a confirmed public-domain status) so the "New Projects Only / original work" and third-party rights rules are never in question during the demo.
