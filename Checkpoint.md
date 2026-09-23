10. I also looked at what's actually left in Vérité

This is the more interesting part.

Your project is not an empty scaffold. There is already a meaningful foundation.

You currently have:

verite/
├── app/
├── frontend/
├── tests/
├── design/
├── docs/
├── infra/
├── scripts/
├── sample_scripts/
├── .github/
├── package.json
├── pyproject.toml
├── Dockerfile
├── firebase.json
├── LICENSE
├── README.md
└── .env.example
What is already implemented

You have a working foundation around:

Screenplay ingestion

Create projects
Upload screenplay
PDF/Fountain/plain-text support
Upload size checking
Empty-file validation
Malformed screenplay handling

Screenplay parser

The parser already extracts things like:

scenes
scene numbers
sluglines
dialogue
characters
props
locations
action

And you already have tests for these.

Processing UI

You have:

Projects
   ↓
New Project
   ↓
Upload screenplay
   ↓
Processing
   ↓
Parsed Scenes

The frontend is actually fairly developed for this stage.

Authentication

There is already Firebase authentication logic supporting:

email/password
Google sign-in
Firebase bearer-token verification on the backend

Persistence

There's already a repository/storage abstraction with local development behavior and Firebase/Cloud infrastructure pieces.

Testing

You already have tests covering things like:

API flow
authentication
screenplay parsing
malformed files
upload size limits
re-uploading
processing states
compliance checking

That's a decent foundation.

11. But there is a BIG gap between the current code and the final architecture

This is what you should know before starting tomorrow.

Your documentation describes the full intended Vérité architecture:

Screenplay
    ↓
Orchestrator
    ↓
Script Parser Agent
    ↓
Entity Extraction Agent
    ↓
Research/Grounding Agent
    ↓
Parallel Search
    ↓
Gemini
    ↓
Continuity & Rights Agent
    ↓
Synthesis Agent
    ↓
Story Bible / Reports

But the actual repository currently doesn't contain those agent/backend layers yet.

For example, the documentation expects:

agents/
    orchestrator.py
    script_parser_agent.py
    entity_extraction_agent.py
    research_agent.py
    continuity_rights_agent.py

backend/
    main.py
    routers/
    services/
        gemini_client.py
        parallel_client.py
        firestore_client.py

Those aren't currently present in the uploaded project.

So the project is currently much closer to M2 than the final product described in the docs.

12. Where you currently are

I'd map the project approximately like this:

Milestone	Current state
M1 — Skeleton/auth	🟢 Mostly done
M2 — Upload + screenplay parsing	🟢 Mostly done
M3 — Entity extraction	🔴 Not implemented as the planned agent
M4 — Parallel grounding	🔴 Not implemented
M5 — Continuity & rights	🔴 Not implemented
M6 — Synthesis/export/polish	🔴 Not implemented
M7 — Demo/submission	🔴 Not started

The biggest unfinished piece is not the UI.

It's the actual intelligence pipeline.

13. What I would do tomorrow

Don't start randomly adding features.

I'd continue in this order:

Phase 1 — Finish the foundation

First make sure:

Upload
   ↓
Parse
   ↓
Scenes

is completely reliable.

Run:

pytest

and make sure the existing test suite passes.

Phase 2 — Entity extraction

Take the scenes you're already generating and extract:

Characters
Props
Locations
Time periods
Real-world claims
Historical references
Technical claims
Legal/rights-sensitive material
Quotes
Brands

For example:

Scene 7

Characters:
- Mara
- Daniel

Props:
- iPhone
- Letter
- Car keys

Location:
- London Underground

Claims:
- "The London Underground opened in 1863."
- "Mara uses an iPhone in 2004."

That last one becomes interesting because it could potentially be an anachronism.

14. Then the most important part: Parallel

This is the part I'd prioritize heavily.

Your docs already identify it as the core integration.

The flow should eventually become:

Screenplay
      ↓
Scene
      ↓
Claim
      ↓
Research Agent
      ↓
Parallel Search
      ↓
Sources
      ↓
Gemini
      ↓
Supported / Contradicted / Unverifiable
      ↓
Citation

For example:

Claim:
"The iPhone was used by Mara in 2004."

Parallel:
→ Apple historical source
→ other reliable sources

Gemini:
→ evaluates the evidence

Result:
CONTRADICTED

Sources:
[actual URLs + snippets]

And crucially, the UI should show the actual evidence.

That is much more compelling than simply saying:

"AI found a problem."

15. Then Continuity & Rights

Once grounding works, you can start doing cross-scene analysis.

For example:

Scene 4:
Mara is 25.

Scene 31:
Mara says she is 32.

→ Continuity flag

Or:

Scene 8:
Mara loses her wedding ring.

Scene 17:
Mara is wearing the same ring.

→ Continuity flag

Or:

Scene 12:
Character quotes copyrighted lyrics.

→ Rights/Clearance flag
16. Then the Story Bible

Eventually your project should produce something like:

VÉRITÉ

PROJECT
The Night Shift

────────────────────────

STORY BIBLE

Characters
Locations
Props
Timeline
Scenes

────────────────────────

FACT CHECK REPORT

12 claims analyzed

✓ 8 supported
⚠ 2 unverifiable
✕ 2 contradicted

────────────────────────

CONTINUITY

7 flags

────────────────────────

RIGHTS & CLEARANCE

3 items requiring review

That becomes the real product rather than simply a screenplay parser.

17. One thing I noticed that we should fix later

Your documentation currently describes the frontend as:

Next.js

and the architecture also says:

Next.js (React)

But the actual frontend in the uploaded project is currently a vanilla JavaScript frontend, with:

frontend/
├── index.html
└── assets/
    ├── app.js
    └── styles.css

That's not necessarily a problem by itself, but it means the documentation and implementation aren't completely synchronized.

Don't worry about fixing that tonight.

Just push the current state.

Tomorrow we can decide whether to:

continue with the current frontend and build the backend/agent pipeline around it, or
migrate the frontend to the intended Next.js architecture.

I wouldn't migrate anything just for the sake of matching the docs until we see whether it actually helps the product.
