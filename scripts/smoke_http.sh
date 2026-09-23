#!/usr/bin/env bash
set -euo pipefail

port="${PORT:-8765}"
sample_script="${1:-sample_scripts/warehouse_fog.fountain}"
if [[ ! -f "$sample_script" ]]; then
  echo "Smoke test failed: sample script does not exist: $sample_script" >&2
  exit 2
fi

data_dir="$(mktemp -d "${TMPDIR:-/tmp}/verite-smoke-data.XXXXXX")"
server_log="$(mktemp "${TMPDIR:-/tmp}/verite-smoke-server.XXXXXX.log")"
server_pid=""

cleanup() {
  if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
  rm -rf -- "$data_dir" "$server_log"
}
trap cleanup EXIT

PYTHONPATH="${PYTHONPATH:-.}" DATA_DIR="$data_dir" AUTH_MODE=local \
  python3 -m uvicorn app.main:app --host 127.0.0.1 --port "$port" >"$server_log" 2>&1 &
server_pid=$!

for attempt in {1..50}; do
  if curl -fsS "http://127.0.0.1:${port}/healthz" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$server_pid" 2>/dev/null; then
    cat "$server_log" >&2
    echo "Smoke test failed: Uvicorn exited before becoming healthy." >&2
    exit 1
  fi
  sleep 0.1
  if [[ "$attempt" == 50 ]]; then
    cat "$server_log" >&2
    echo "Smoke test failed: service did not become healthy." >&2
    exit 1
  fi
done

SAMPLE_SCRIPT="$sample_script" SMOKE_PORT="$port" node --input-type=module <<'NODE'
import fs from "node:fs";

const base = `http://127.0.0.1:${process.env.SMOKE_PORT}`;
const sample = process.env.SAMPLE_SCRIPT;

const healthResponse = await fetch(`${base}/healthz`);
const health = await healthResponse.json();
const projectResponse = await fetch(`${base}/api/projects`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ title: "Warehouse Fog HTTP Smoke Test" }),
});
const project = await projectResponse.json();
if (!projectResponse.ok) throw new Error(`project creation failed: ${projectResponse.status}`);

const form = new FormData();
form.append("file", new Blob([fs.readFileSync(sample)], { type: "text/plain" }), "warehouse_fog.fountain");
const uploadResponse = await fetch(`${base}/api/projects/${project.id}/scripts`, { method: "POST", body: form });
const initial = await uploadResponse.json();
if (!uploadResponse.ok) throw new Error(`upload failed: ${uploadResponse.status}: ${JSON.stringify(initial)}`);

let final = initial;
for (let attempt = 0; attempt < 100 && final.status === "processing"; attempt += 1) {
  await new Promise((resolve) => setTimeout(resolve, 50));
  final = await (await fetch(`${base}/api/projects/${project.id}`)).json();
}

const evidence = {
  health_status: healthResponse.status,
  health,
  project_status: projectResponse.status,
  upload_status: uploadResponse.status,
  initial_status: initial.status,
  initial_scene_count: initial.scenes.length,
  final_status: final.status,
  filename: final.script?.filename,
  scene_count: final.scenes?.length ?? 0,
  sluglines: (final.scenes ?? []).map((scene) => scene.slugline),
};
console.log(JSON.stringify(evidence, null, 2));

if (
  health.status !== "ok" ||
  projectResponse.status !== 201 ||
  uploadResponse.status !== 201 ||
  initial.status !== "processing" ||
  final.status !== "ready" ||
  final.script?.filename !== "warehouse_fog.fountain" ||
  final.scenes?.length !== 2
) {
  process.exit(1);
}
NODE
