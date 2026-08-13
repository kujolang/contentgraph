# ContentGraph 0.3.0 completion audit

| Requirement | Evidence |
| --- | --- |
| Consented real field campaign | `scripts/prepare-field-corpora.kujo`, `scripts/field-benchmark.kujo`, pinned/redacted manifest, three 5,000-page result profiles with medians, variances, RSS, shape, hardware, and thresholds. |
| Streaming publication | Direct incremental JSON/JSONL staging writes, bounded schema validation, output budgets, SHA-256 manifest, cleanup on failure, atomic rename, unchanged public golden bytes, and a three-run pinned field comparison showing median peak RSS falls 13.86% (596,676,608 to 513,957,888 bytes). |
| Adapter cache | Independently fingerprinted SiteProbe, sitemap, CSV, and CMS parsed results; integrity validation; hit/miss diagnostics; cold/partial-warm benchmark. |
| Vendor mappings | Offline stable-contract WordPress, Contentful, Sanity, Drupal, and generic SQL examples; all five pass native tests without network. |
| Explainability | `explain` traces cluster, overlap, bridge, or link evidence with 1–100 result and per-string bounds, runtime schema validation, deterministic tests, and no mutation authority. |
| Tokenizer profiles | Explicit deterministic ASCII default and Unicode letter/number v1 profile; cache invalidation; mixed-script fixture; golden default preservation. |
| SARIF | Deterministic SARIF 2.1.0 subset validation, 1–5,000 bound, three documented severity rules, output equality tests, and `automaticMutation: false`. |
| Distribution | Official Kujo 1.0.1 assets verified before four platform bundles; Homebrew/Scoop manifests; checksums, provenance, SBOM, OIDC attestation, rollback. |
| Static demo | Kujo-generated offline HTML, CSP, accessible filtering, byte test, and evidence/source links for every visible conclusion. |
| Local telemetry | Explicit opt-in only; runtime schema prohibits undeclared fields; no content/URL/query/network collection; manifest hash; deterministic mode exclusion. |
| Compatibility | v1 legacy reads retained; 0.2 missing adapter cache handled additively; incremental manifest integrity checked before any cache reuse. |

Every item and exit criterion from `docs/next-session-review-0.3.md` is complete.
No Python implementation or benchmark helper remains; core source, tests,
benchmarking, demo generation, contracts, and packaging orchestration are Kujo.
