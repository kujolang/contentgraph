# ContentGraph next-session review (0.3)

The 0.2 production-hardening checklist is complete. These are additive product
opportunities for the next review, not 0.2 release blockers.

## P1 — field validation and scale

- [x] Run a consented, redacted benchmark campaign on several real 5k–20k page
  corpora and publish medians, variance, peak RSS, corpus shape, hardware, and
  regression thresholds without mixing synthetic and field results.
- [x] Stream large JSON/JSONL artifact serialization directly into the staging
  directory while preserving atomic publication, byte determinism, schema
  validation, manifest integrity, and output-budget enforcement.
- [x] Add per-adapter parse-cache reuse for partially changed SiteProbe, CSV,
  sitemap, and CMS inputs, with cache-hit diagnostics and cold/warm benchmarks.

## P2 — universal integrations and explainability

- [x] Publish first-party mapping examples for WordPress, Contentful, Sanity,
  Drupal, and generic SQL exports using the stable CMS contract rather than
  embedding vendor-specific network clients.
- [x] Add an `explain` command that traces a cluster, overlap, bridge, or link
  recommendation to bounded terms and measured evidence in agent-safe JSON.
- [x] Design versioned tokenizer profiles for non-English and mixed-script
  corpora while retaining the deterministic lexical default and golden fixtures.
- [x] Add optional SARIF output for policy-driven CI findings with documented
  severity rules and zero automatic content mutation.

## P3 — distribution and ecosystem presentation

- [x] Produce checksum-verified platform launch bundles and package-manager
  manifests once Kujo's binary distribution contract is stable.
- [x] Publish an interactive, static demo generated from the public corpus that
  links every visible conclusion to its ContentGraph artifact and Kujo source.
- [x] Add an opt-in local telemetry contract for timing and resource diagnostics;
  keep the default offline and prohibit content, URL, and query collection.

## Exit criteria for the next review

- Field benchmarks are reproducible and clearly separated from synthetic data.
- Large-run peak memory is materially lower without changing golden output.
- At least two vendor mappings pass contract fixtures without network access.
- Explainability and any SARIF output remain deterministic, bounded, and tested.
- Distribution changes preserve signed provenance, rollback, and v1 read compatibility.
