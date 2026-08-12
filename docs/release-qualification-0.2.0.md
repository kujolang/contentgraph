# ContentGraph 0.2.0 release qualification

Status: locally qualified; remote CI and artifact attestation are verified from
the tagged release after publication.

The native Kujo validation covers byte-golden deterministic output, runtime
JSON Schema contracts, configuration precedence, adapters, GraphML query-node
integrity, incremental equivalence and invalidation, graph analysis, duplicate
canonicals, Unicode preservation, high-cardinality metadata, resource failure,
source immutability, comparisons, and malformed stored artifacts.

## Synthetic scale profile

Command: `../kujo/target/release/kujo run scripts/profile-scale.kujo`

Environment: macOS 26.3, Intel Core i7-9750H (12 logical CPUs), 16 GiB RAM,
Kujo 1.0.1. This is a local regression profile, not a cross-product marketing
benchmark. The generated corpus deliberately contains five terms in every
document; `--max-term-document-frequency-ratio 0.05` filters those terms before
candidate generation. Timings and peak RSS are from `/usr/bin/time`.

| Nodes | Seconds | Peak RSS | Output bytes | Candidate pairs |
| ---: | ---: | ---: | ---: | ---: |
| 5,000 | 112.811 | 473,399,296 | 6,604,392 | 0 |
| 10,000 | 295.285 | 1,095,385,088 | 12,749,404 | 0 |
| 20,000 | 1,049.929 | 1,606,352,896 | 25,109,406 | 0 |

The profile proves the documented hard ceiling is repeatable on the stated
machine. Candidate-heavy behavior is separately bounded and adversarially
tested by `max_candidate_pairs`; real-corpus medians remain a 0.3 opportunity.

## Local release gates

- Native validation, 17 schema checks, golden compatibility, and adversarial
  tests: pass.
- Deterministic 1,000-node benchmark gate: pass.
- Reproducible archive, checksum, CycloneDX SBOM, and provenance generation:
  pass; two clean invocations produced archive SHA-256
  `ae83c78c35ef8aaae4af70900b1681afae8431b33c4760710647a7ea91b62b45`,
  and every `SHA256SUMS` entry verified.
- Upgrade/rollback and v0.1 read compatibility: documented and tested.
- Scoped source/security review: no open high-severity finding.
