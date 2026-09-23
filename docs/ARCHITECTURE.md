# ARCHITECTURE.md — Vérité

## 1. System overview

Vérité is a multi-agent pipeline, orchestrated on **Google Cloud Agent Builder / Agent Development Kit (ADK)**, that turns an uploaded screenplay into a cited, continuity-checked **Story Bible**. Reasoning is done by **Gemini**; grounding is done by **Parallel's Search API**.

```
                      ┌─────────────────────────────────────────────┐
                      │              Vérité Web App                 │
                      │        (Next.js, Cloud Run / Firebase)      │
                      └───────────────────┬───────────────────────-─┘
                                           │ REST/streaming
                      ┌────────────────────▼──────────────────────┐
                      │        Orchestrator Agent (ADK)            │
                      │   Gemini 2.x on Vertex AI — plans & routes │
                      └──┬───────┬───────────┬──────────┬─────────┘
             ┌───────────┘       │           │          └──────────────┐
             ▼                   ▼           ▼                         ▼
   ┌──────────────────┐ ┌───────────────┐ ┌─────────────────┐ ┌──────────────────┐
   │ 1. Script Parser  │ │ 2. Entity     │ │ 3. Research /    │ │ 4. Continuity     │
   │    Agent          │ │   Extraction  │ │   Grounding Agent│ │   & Rights Agent  │
   │ Gemini            │ │   Agent       │ │ Gemini + Parallel│ │ Gemini            │
   │                   │ │ Gemini        │ │ Search API       │ │                   │
   └──────────────────┘ └───────────────┘ └─────────────────┘ └──────────────────┘
             │                   │                   │                    │
             └───────────────────┴─────────┬─────────┴────────────────────┘
                                            ▼
                                ┌───────────────────────┐
                                │  5. Synthesis Agent    │
                                │  Gemini — compiles the │
                                │  Story Bible report    │
                                └───────────┬────────────┘
                                            ▼
                                ┌───────────────────────┐
                                │   Firestore (state)    │
                                │   Cloud Storage (docs) │
                                └───────────────────────┘
```

## 2. Agents in detail

### 2.1 Script Parser Agent
- **Input:** uploaded screenplay (PDF, Fountain, or plain text).
- **Job:** normalize into scene units (slugline, action, dialogue, scene number) using Gemini's long-context understanding. Screenplay format is fairly regular (INT./EXT., ALL CAPS character cues) so this is a structuring task, not free generation.
- **Output:** `Scene[]` objects written to Firestore.

### 2.2 Entity Extraction Agent
- **Input:** parsed scenes.
- **Job:** for each scene, extract: characters present, props referenced, locations, time period/era markers, and any **factual or verifiable claims** (real places, historical events, technical/legal/medical details, quoted material, brand/trademark mentions).
- **Output:** `Entity[]` and `Claim[]` linked to scene IDs. A claim gets a `needs_grounding: true` flag if it references the real world (as opposed to purely fictional content).

### 2.3 Research / Grounding Agent — **primary Parallel integration point**
- **Input:** flagged `Claim[]`.
- **Job:** for each claim, call **Parallel's Search API** (via the official `parallel-web` SDK) to retrieve current, cited sources. Gemini then reads the search results and produces a verdict: `Supported / Contradicted / Unverifiable`, a confidence score, and the source citations.
- **This is the load-bearing integration for the track requirement** — it must be a real, imported SDK call in the agent's actual execution path (see `docs/AUDIT.md` §2 and `docs/IMPLEMENTATION.md` for the exact file).
- **Example claim types this catches:** "a 1987 scene shows a character using a smartphone" (anachronism), "a line attributes a real historical event to the wrong year," "a quoted song lyric that may not be public domain," "a location described with real-world geography that's actually inaccurate."

### 2.4 Continuity & Rights Agent
- **Job:** cross-scene reasoning (Gemini, using the full Story Bible as context) — does a prop introduced in scene 12 disappear without explanation in scene 40? Does a character's stated age contradict an earlier scene? Does dialogue quote copyrighted material (song lyrics, poems) that would need clearance? Flags are ranked by production risk (continuity / legal / factual).

### 2.5 Synthesis Agent
- **Job:** compiles everything into the final Story Bible: per-scene breakdown, character/location/prop indices, a **Fact-Check Report** (from 2.3) and a **Continuity & Clearance Report** (from 2.4), each citation traceable back to its Parallel search source.

## 3. Data model (Firestore, simplified)

```
projects/{projectId}
  ├─ title, createdAt, ownerId, status
  └─ scripts/{scriptId}
       ├─ rawFileRef (Cloud Storage path)
       └─ scenes/{sceneId}
            ├─ sceneNumber, slugline, synopsis
            ├─ characters: [entityId]
            ├─ props: [entityId]
            ├─ locations: [entityId]
            └─ claims/{claimId}
                 ├─ text, type (historical|technical|legal|quote|geography)
                 ├─ verdict, confidence
                 └─ sources: [{title, url, snippet, retrievedAt}]  ← from Parallel
```

## 4. Tech stack

| Layer            | Choice                                                              |
|-------------------|----------------------------------------------------------------------|
| Orchestration     | Google Cloud Agent Builder / ADK (Python)                           |
| Reasoning model   | Gemini 2.x via `google-genai` / `google-cloud-aiplatform`            |
| Grounding search  | Parallel Search API via `parallel-web` SDK                           |
| Backend API       | FastAPI on Cloud Run                                                 |
| Frontend          | Next.js (React), deployed to Cloud Run or Firebase Hosting           |
| Data store        | Firestore (structured data), Cloud Storage (raw script files)        |
| Auth              | Firebase Auth (email + Google sign-in)                               |
| Observability     | Cloud Logging / Cloud Trace (built-in, no partner dependency)        |

## 5. Why a multi-agent design (not one big prompt)

Judging criterion "Technological Implementation" rewards showing *how effectively* the tools are used, not just that they're called once. Splitting parsing, extraction, grounding, and continuity into separate agents:
- keeps each Gemini call's context small and reliable (long screenplays don't fit well in one pass),
- makes the **Parallel** call auditable as its own step with its own inputs/outputs (important for the runtime-usage requirement),
- lets the UI show live "agent trace" progress, which is also a strong demo moment for the video.

## 6. What's explicitly out of scope for the hackathon build

To keep this achievable in the contest window:
- No real screenplay-format editor (Final Draft-style) — upload/parse only.
- No production scheduling/budgeting features — that's a different product.
- No multi-tenant billing — single workspace per team is enough for the demo.
