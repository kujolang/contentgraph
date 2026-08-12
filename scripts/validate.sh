#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KUJO_RUNTIME="${KUJO_BIN:-$ROOT/../kujo/target/release/kujo}"
cd "$ROOT"
"$KUJO_RUNTIME" check src/main.kujo
"$KUJO_RUNTIME" check src/text.kujo
"$KUJO_RUNTIME" check src/contracts.kujo
"$KUJO_RUNTIME" check src/ingest.kujo
"$KUJO_RUNTIME" check src/analytics.kujo
"$KUJO_RUNTIME" check src/engine.kujo
"$KUJO_RUNTIME" check scripts/benchmark.kujo
"$KUJO_RUNTIME" check scripts/profile-scale.kujo
"$KUJO_RUNTIME" check scripts/package-release.kujo
"$KUJO_RUNTIME" check scripts/validate-schemas.kujo
for source in src/*.kujo scripts/*.kujo tests/*.kujo; do "$KUJO_RUNTIME" lint "$source" >/dev/null; done
"$KUJO_RUNTIME" run tests/contentgraph_tests.kujo
./contentgraph doctor >/dev/null
"$KUJO_RUNTIME" run scripts/validate-schemas.kujo
bash scripts/diff-check.sh
printf 'ContentGraph validation passed.\n'
