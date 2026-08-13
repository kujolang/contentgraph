# Benchmark evidence

Synthetic capacity results and field results are intentionally separate:

- `synthetic-scale-0.3.json` covers generated stress shapes and memory comparison.
- `adapter-cache-0.3.json` covers deterministic fixture cold/partial-warm reuse.
- `field-corpora.json` pins public source commits, license-based consent,
  redaction policy, hardware, settings, and regression thresholds.
- `field-results-0.3.json` contains repeated field measurements only; it never
  contains source text, URLs from pages, or queries.
- `streaming-memory-field-0.3.json` compares the 0.2.1 and 0.3.0 publishers on
  the same pinned, redacted MDN Web API sample and enforces a 5% median peak-RSS
  reduction gate.

Reproduce field results after preparing the exact manifest commits and exported
environment paths:

```bash
kujo run scripts/prepare-field-corpora.kujo -- --out /tmp/contentgraph-field
export CONTENTGRAPH_FIELD_MDN_API=/tmp/contentgraph-field/mdn-api
export CONTENTGRAPH_FIELD_MDN_NON_API=/tmp/contentgraph-field/mdn-non-api
export CONTENTGRAPH_FIELD_MDN_MIXED=/tmp/contentgraph-field/mdn-mixed
kujo run scripts/field-benchmark.kujo -- \
  --manifest benchmarks/field-corpora.json \
  --out benchmarks/field-results-0.3.json \
  --repeats 3

# Compare 0.2.1 to the recorded 0.3 field profile. The first invocation runs
# the pinned 0.2.1 launcher three times; later checks can reuse that receipt.
kujo run scripts/streaming-memory-comparison.kujo -- \
  --baseline-launcher /path/to/contentgraph-0.2.1/contentgraph \
  --corpus "$CONTENTGRAPH_FIELD_MDN_API" \
  --field-results benchmarks/field-results-0.3.json \
  --out benchmarks/streaming-memory-field-0.3.json \
  --repeats 3
kujo run scripts/streaming-memory-comparison.kujo -- \
  --baseline-results benchmarks/streaming-memory-field-0.3.json \
  --field-results benchmarks/field-results-0.3.json \
  --out benchmarks/streaming-memory-field-0.3.json
```

Acquisition may require network access; ContentGraph execution remains offline.
Do not benchmark private material without explicit authorization and redaction.
