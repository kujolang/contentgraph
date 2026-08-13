#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KUJO_RUNTIME="${KUJO_BIN:-$ROOT/../kujo/target/release/kujo}"
export CONTENTGRAPH_KUJO_BIN="$KUJO_RUNTIME"
cd "$ROOT"
for source in src/*.kujo scripts/*.kujo tests/*.kujo; do
  "$KUJO_RUNTIME" check "$source"
  "$KUJO_RUNTIME" lint "$source" >/dev/null
done
"$KUJO_RUNTIME" run tests/contentgraph_tests.kujo
if [[ "${CONTENTGRAPH_WINDOWS_LAUNCHER:-}" == "1" ]]; then
  cmd.exe /d /c contentgraph.cmd doctor >/dev/null
else
  ./contentgraph doctor >/dev/null
fi
"$KUJO_RUNTIME" run scripts/validate-schemas.kujo
bash scripts/diff-check.sh
printf 'ContentGraph validation passed.\n'
