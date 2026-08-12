# Next-session engineering review

This is the prioritized follow-up list after the production-hardening review.
Items are intentionally unimplemented; each needs its own scoped design and
verification pass.

## P0 — Kujo showcase and contract integrity

- Port tokenization, frontmatter extraction, sparse TF-IDF scoring, union-find,
  and artifact serialization from `src/contentgraph.py` into Kujo modules. Keep
  golden fixtures proving byte-level compatibility before removing Python.
- Add runtime JSON Schema validation of every emitted artifact and accepted
  SiteProbe/SearchBridge contract. The repository currently validates schema
  syntax, while Python tests assert selected output fields.
- Define a versioned configuration file contract so enterprise users can store
  thresholds and budgets without long command lines; specify CLI-over-config
  precedence and reject unknown keys.

## P1 — Scale, interoperability, and analysis depth

- Replace the in-memory candidate-score map with a bounded streaming/top-k
  accumulator and profile 5k, 10k, and 20k-node corpora with high-frequency
  terms. Preserve deterministic ordering across worker counts.
- Add sitemap/XML, CSV, and structured CMS export adapters behind explicit,
  versioned input contracts; do not turn ContentGraph into a crawler.
- Emit GraphML query nodes or a documented separate query-edge export so search
  associations are represented without dangling endpoints.
- Add component-level centrality, bridge-page, hub/authority, crawl-depth drift,
  and cluster-health reports with deterministic methods and bounded complexity.
- Add incremental builds keyed by input fingerprints, including explicit cache
  invalidation and equivalence tests against clean builds.

## P2 — Enterprise operations and presentation

- Publish signed, reproducible Kujo/ContentGraph release artifacts with an SBOM,
  checksums, provenance, supported-platform matrix, and rollback instructions.
- Add Windows validation plus macOS/Linux release-matrix tests for path,
  encoding, executable-launcher, and GraphML behavior.
- Add property-based artifact invariants and differential tests for comparison,
  clustering, duplicate canonical URLs, Unicode normalization, and adversarial
  high-cardinality metadata.
- Create a small public demonstration corpus and checked-in expected report so
  prospective Kujo users can understand the value without supplying private
  site data.
- Add a machine-readable `doctor --json` compatibility report covering Kujo and
  Python versions, filesystem permissions, and safe resource-limit guidance.

## Exit criteria for an enterprise-readiness claim

- The deterministic engine is native Kujo or the remaining compatibility layer
  has a published support/deprecation policy.
- Schema validation, cross-platform CI, reproducible signed releases, SBOM, and
  large-corpus performance envelopes are independently repeatable.
- No high-severity security findings are open, upgrade/rollback procedures are
  documented, and all public contracts have backward-compatibility tests.
