# ADR 0001: M2 parser and persistence boundaries

## Decision

Milestone 2 uses a deterministic screenplay structure parser behind `app/parser.py`, with a stable `Scene` model exposed by the API. Uploads transition to `processing` and are parsed by a bounded in-process `ThreadPoolExecutor`; the frontend polls the project endpoint until `ready` or `error`. Local JSON/filesystem persistence is the development fallback; Firestore and Cloud Storage adapters activate when the corresponding Google Cloud environment variables are configured. Replacing `scripts/latest/scenes` first deletes existing scene documents, then writes the new set.

## Why

This keeps upload and parsing usable in a clean Cloud Run or local environment without requiring model credentials for the first demonstrable milestone. The background job makes the processing page truthful without artificial delays: the API returns after storage and job submission, and the UI observes the persisted status. Screenplay scene headings and dialogue conventions are sufficiently regular for reliable structural extraction, while later semantic work can be added as a separate agent.

## Alternatives considered

- Calling a hosted model during upload would make M2 dependent on credentials, latency, and quota, and would blur the boundary with later entity/grounding milestones.
- Persisting only in process memory would lose uploaded scripts whenever Cloud Run scales or restarts.
- A durable task queue would survive instance termination better, but is unnecessary infrastructure for this M2 parser and is not available in the current deployment scaffold. The executor is bounded and the result is persisted as soon as parsing completes.

## Later integration compatibility

The upload endpoint, `Scene` schema, processing log, polling contract, and repository interface are independent of the parser implementation. A later Gemini/ADK parser or Parallel-backed research stage can consume the stored scenes without changing the M2 UI contract. No Parallel or grounding behavior is implemented here.
