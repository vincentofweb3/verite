# Vérité

Vérité is a screenplay processing workspace for the Google Cloud Agentic Cinema hackathon. Milestones 1 and 2 provide the application foundation, authentication configuration, upload handling, storage boundaries, and real screenplay-to-scenes parsing flow. Research, citations, entity extraction, continuity, and Parallel grounding are intentionally not included yet.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
cp .env.example .env
uvicorn app.main:app --reload
```

Open <http://localhost:8000>. With the default `AUTH_MODE=local`, the app uses a local demo workspace. For a deployed Firebase-authenticated service, set `AUTH_MODE=firebase`, provide Firebase web configuration in `FIREBASE_WEB_CONFIG`, and deploy with Google Application Default Credentials so the backend can verify ID tokens.

## M2 demo

Use `sample_scripts/warehouse_fog.fountain`, or upload a `.txt`, `.fountain`, or text-based `.pdf` screenplay from **New project**. The service stores the original upload, returns a truthful `processing` project state, parses the file in a bounded background worker, and exposes the persisted result for frontend polling. Parsed scene headings, action, dialogue, characters, simple props, and locations render in the processing and parsed-script views.

## Checks

```bash
bash scripts/check_compliance.sh
python -m compileall -q app tests
pytest
```

The compliance gate scans shipped application source for prohibited non-Google AI vendor references. It is also run by `.github/workflows/ci.yml`.

Firestore rules tests are defined in `tests/firestore-rules.mjs` and run with `npm run test:rules` when Java and the Firebase CLI dependencies are available. The current source-level rules test also checks the create/update ownership split.

To reproduce the local HTTP M2 smoke test with the real sample screenplay, install the Python test dependencies and run:

```bash
bash scripts/smoke_http.sh sample_scripts/warehouse_fog.fountain
```

The command starts a temporary Uvicorn service, creates a local project, uploads the sample, polls the persisted processing state, prints the two parsed scene sluglines, and cleans up its temporary data.

## Cloud Run

Build and deploy the single-service container (the static frontend is served by FastAPI):

```bash
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/verite/verite:latest
gcloud run deploy verite --image REGION-docker.pkg.dev/PROJECT_ID/verite/verite:latest --region REGION --allow-unauthenticated
```

Configure `GCP_PROJECT_ID`, `GCS_BUCKET`, `AUTH_MODE`, and `FIREBASE_WEB_CONFIG` in Cloud Run. `infra/cloudrun-backend.yaml` is a deployment template; replace its placeholders before applying it. The app uses Cloud Storage and Firestore when configured and a local fallback otherwise.

## Scope handoff

M3 entity extraction and M4 Parallel/Gemini grounding are deliberately left for the next implementation phase. No citation UI or fabricated research output is present in this milestone.
