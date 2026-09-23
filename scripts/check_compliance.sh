#!/usr/bin/env bash
set -euo pipefail

if (($#)); then
  scan_roots=("$@")
else
  # Keep this list limited to shipped source directories. Optional future
  # directories must not make the gate silently skip the scan.
  scan_roots=(app frontend)
fi

for scan_root in "${scan_roots[@]}"; do
  if [[ ! -e "$scan_root" ]]; then
    echo "Compliance check failed: scan root does not exist: $scan_root" >&2
    exit 2
  fi
done

set +e
rg -n -i --glob '*.py' --glob '*.ts' --glob '*.tsx' --glob '*.js' --glob '*.jsx' \
  'openai|anthropic|api\.openai\.com|api\.anthropic\.com' "${scan_roots[@]}" 2>/dev/null
rg_status=$?
set -e

if [[ "$rg_status" -eq 0 ]]; then
  echo 'Disallowed AI vendor reference found in shipped source.' >&2
  exit 1
elif [[ "$rg_status" -ne 1 ]]; then
  echo "Compliance check failed: scanner error (rg exit $rg_status)." >&2
  exit 2
fi
echo 'Compliance check passed: no disallowed AI vendor references in shipped source.'
