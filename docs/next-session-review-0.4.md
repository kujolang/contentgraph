# ContentGraph next-session review (0.4)

ContentGraph 0.3 completes the field-validation, streaming, explainability,
distribution, and ecosystem-presentation objectives. These are additive 0.4
opportunities, not 0.3 release blockers.

## P1 — sustained scale and operations

- [ ] Add a consent workflow for private field corpora that emits only signed,
  aggregate benchmark receipts and automatically proves redaction policy.
- [ ] Introduce bounded cache compaction/eviction policies with dry-run impact
  reports for long-lived incremental run chains.
- [ ] Evaluate Kujo-native parallel tokenization shards while retaining stable
  ordering, identical artifact bytes, and explicit CPU/memory ceilings.

## P2 — analysis depth and interoperability

- [ ] Add schema-mapped offline exports for common analytics warehouses and
  graph stores without introducing vendor credentials or runtime networking.
- [ ] Add deterministic explanation diffs between two runs so CI can state why
  a cluster, bridge, overlap, or recommendation changed.
- [ ] Add opt-in locale-specific stop-word profiles with public fixtures,
  versioned provenance, and cross-platform byte-golden coverage.

## P3 — adoption and ecosystem

- [ ] Publish official package repositories/taps after the platform bundles have
  completed one release cycle and install/upgrade/rollback smoke tests.
- [ ] Add a larger public interactive showcase with precomputed filters and an
  accessibility audit while keeping it static and network-independent.
- [ ] Define an optional OpenTelemetry file-export bridge that consumes only the
  privacy-restricted local telemetry contract and remains disabled by default.

## Exit criteria for the next review

- Private benchmark receipts cannot disclose page text, URLs, or query values.
- Parallel or compacted runs remain byte-identical to the sequential baseline.
- Explanation diffs and locale profiles are deterministic, bounded, and tested.
- Package repository installs preserve checksums, attestations, and rollback.
- All new bridges remain offline-first and require explicit operator opt-in.
