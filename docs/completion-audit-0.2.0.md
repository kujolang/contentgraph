# ContentGraph 0.2.0 completion audit

This record maps the production-hardening review to implementation and
repeatable evidence. The release gate is `bash scripts/validate.sh`; all source,
test, benchmark, schema, and packaging logic is implemented in Kujo except the
small cross-platform launchers and standard archive/process utilities.

| Requirement | Evidence |
| --- | --- |
| Native engine | `src/text.kujo`, `src/ingest.kujo`, `src/engine.kujo`, and `src/analytics.kujo`; the Python engine and tests were removed. |
| Deterministic compatibility | Checked-in byte-golden run, native primitive oracle, deterministic rerun comparison, and 0.1 read compatibility. |
| Runtime contracts | `src/contracts.kujo`, 17 published schemas, strict versioned config, input-boundary validation, output-boundary validation, and manifest integrity checks. |
| Bounded performance | Sparse per-source scoring, per-node top-k retention, document-frequency filtering, candidate/input/output/node caps, atomic publication, and 5k/10k/20k CPU-memory profiles. |
| Adapters | Versioned source, SiteProbe, SearchBridge, sitemap XML, CSV, and structured CMS contracts recorded in metadata. ContentGraph does not crawl. |
| Graph semantics | GraphML query nodes prevent dangling endpoints; analysis covers components, degree centrality, bridges, hubs, authorities, crawl-depth drift, and cluster health. |
| Incremental operation | Path/size/SHA-256 dependency fingerprints, exact artifact reuse, unchanged tokenization reuse after partial changes, invalidation, and byte-equivalence tests. |
| Robustness | Property/differential cases cover duplicates, Unicode, high-cardinality metadata, malformed runs, caps, source immutability, comparisons, and legacy behavior. |
| Platforms | Linux, macOS, and Windows CI; the Windows `.cmd` launcher is exercised separately. |
| Supply chain | SHA-pinned actions, locked Kujo build, deterministic archive, SHA-256 checksums, CycloneDX SBOM, SLSA-shaped provenance, and GitHub OIDC artifact attestation. |
| Operations | Machine-readable doctor report, compatibility policy, demo, methodology, security boundaries, platform matrix, and upgrade/rollback runbook. |

No high-severity security finding remained open after the offline capability,
path, contract, resource-bound, output-integrity, workflow-permission, and
dependency-pin review. This is a scoped source review, not a third-party
penetration-test claim.
