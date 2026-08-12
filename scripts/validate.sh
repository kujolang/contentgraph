#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KUJO_RUNTIME="${KUJO_BIN:-$ROOT/../kujo/target/release/kujo}"
cd "$ROOT"
python3 -m py_compile src/contentgraph.py tests/test_contentgraph.py
python3 tests/test_contentgraph.py
"$KUJO_RUNTIME" check src/main.kujo
"$KUJO_RUNTIME" check scripts/benchmark.kujo
"$KUJO_RUNTIME" run tests/contentgraph_tests.kujo
./contentgraph doctor >/dev/null
for schema in schemas/*.json; do python3 -m json.tool "$schema" >/dev/null; done
git diff --check
printf 'ContentGraph validation passed.\n'
