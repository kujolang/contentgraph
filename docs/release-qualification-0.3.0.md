# ContentGraph 0.3.0 release qualification

Status: qualified for tagged publication after local gates and hosted release
workflows pass. GitHub release assets remain the source of record for remote CI,
checksums, SBOM, provenance, and build attestations.

## Field benchmark campaign

The campaign uses three distinct 5,000-page samples from pinned MDN public
content commit `8a10694edf44bde124fa8f18af65651855f632dc`. Upstream CC-BY-SA licensing is
the consent basis. Preparation excludes `.git`/private overlays, removes
frontmatter URL identities, replaces URL/email-like values, and caps each real
page excerpt at 512 characters. Only aggregate results are committed.

Hardware: MacBookPro16,1; 6-core Intel Core i7 2.6 GHz (12 logical CPUs);
16 GiB RAM; macOS 26.3.1; local APFS; Kujo 1.0.1. Three cold runs per corpus,
`max_term_document_frequency_ratio=0.0`, two-million candidate-pair ceiling.

| Field corpus | Pages | Median seconds | Seconds variance | Median peak RSS | RSS variance | Median output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MDN Web API | 5,000 | 326.477 | 4,547.023 | 513,957,888 | 1,982,958,811,364 | 8,851,935 |
| MDN non-API | 5,000 | 507.404 | 3,329.368 | 523,575,296 | 160,886,794,281,870 | 8,964,590 |
| MDN mixed | 5,000 | 424.364 | 8,158.917 | 519,778,304 | 427,806,596,588,430 | 8,893,471 |

Thresholds: median at most 600 seconds per 5,000 pages, peak RSS at most 1 GiB,
and seconds variance at most 10,000. All pass. This field campaign is explicitly
separate from `benchmarks/synthetic-scale-0.3.json`. The aggressive ratio removes
all document-shared terms in this specific campaign, so candidate pairs are zero;
the corpus still exercises real parsing, tokenization, graph materialization,
streamed publication, cache serialization, schemas, hashing, and atomic commit.

## Streaming and cache evidence

Large artifact files are validated in bounded batches and written incrementally
to a private staging directory before hash, output-budget, manifest, and rename
gates. Public graph, node, edge, cluster, overlap, orphan, link-opportunity,
analysis, and report golden bytes remain equal to 0.2.1.

The like-for-like MDN Web API comparison records three cold 0.2.1 runs and the
three cold 0.3.0 field runs under identical corpus and scoring settings. Median
peak RSS falls from 596,676,608 to 513,957,888 bytes, a 13.86% reduction that
passes the explicit 5% material-improvement gate. The Kujo comparison receipt is
`benchmarks/streaming-memory-field-0.3.json`.

The synthetic 5,000-node before/after shape remains memory-neutral because 0.3
adds a parsed CSV cache and grows output from 5.82 MB to 9.08 MB; the record does
not misrepresent this synthetic shape as a streaming win. Partial adapter reuse
reports three hits and one miss after one changed adapter; fixture cold/warm
medians are 0.194 and 0.195 seconds, where tiny inputs make parsing savings
smaller than process noise.

## Local release gates

- Native validation, 21 schema checks, deterministic golden, adversarial,
  adapter-cache, explainability, tokenizer, telemetry, CMS mapping, SARIF,
  compatibility, and static-demo tests: pass.
- Deterministic 1,000-node benchmark: pass.
- Portable archive plus Linux/macOS/Windows runtime bundles, Homebrew/Scoop
  manifests, checksums, CycloneDX SBOM, SLSA-shaped provenance: pass locally.
- v1 read compatibility, 0.2 incremental compatibility, integrity failure,
  signed provenance, and rollback procedure: documented and tested.
