# ContentGraph

[![Version](https://img.shields.io/badge/version-0.3.0-black)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![built with Kujo](https://img.shields.io/badge/built%20with-Kujo-white.svg)](https://github.com/kujolang/kujo)

ContentGraph builds a deterministic, inspectable network of relationships among
website pages and local content. SiteProbe discovers pages, SearchBridge adds
measured search evidence, and ContentGraph connects the corpus without a hosted
service, model key, paid API, or network request.

It is useful for information-architecture review, internal-link discovery,
orphan detection, topic exploration, overlap triage, release comparisons, and
agent workflows that need evidence rather than opaque recommendations.

## Requirements and installation

- Kujo 1.0 or newer. By default the launchers use
  `../kujo/target/release/kujo`; set `KUJO_BIN` to use another binary.
- No Python, third-party packages, model keys, or hosted services.

```bash
git clone https://github.com/kujolang/contentgraph.git
cd contentgraph
export KUJO_BIN=/absolute/path/to/kujo
./contentgraph doctor
```

`doctor` is JSON by default; `./contentgraph doctor --json` is accepted for
explicit automation intent.

The complete engine, CLI, contracts, adapters, analytics, tests, benchmark, and
release packager are implemented directly in Kujo under `src/` and `scripts/`.

## Quick start

```bash
./contentgraph build --source ./content --out .contentgraph/baseline
./contentgraph orphans .contentgraph/baseline
./contentgraph related .contentgraph/baseline --node guides/getting-started.md
./contentgraph link-opportunities .contentgraph/baseline
./contentgraph explain .contentgraph/baseline --type cluster --id cluster-001 --limit 10
./contentgraph export .contentgraph/baseline --format graphml --out graph.graphml
./contentgraph export .contentgraph/baseline --format sarif --limit 500 --out contentgraph.sarif
```

Inputs can be repeated and combined:

```bash
./contentgraph build \
  --siteprobe /path/to/.siteprobe/run \
  --source ./docs \
  --sitemap ./sitemap.xml \
  --csv ./content-export.csv \
  --cms ./cms-export.json \
  --searchbridge /path/to/search-performance.json \
  --out .contentgraph/combined
```

Store repeatable build settings in a versioned TOML or JSON file and override
individual values on the command line:

```bash
./contentgraph build --config contentgraph.example.toml --max-nodes 10000
```

Source discovery accepts Markdown, HTML, JSON, and text files, ignores known
generated/dependency directories, rejects symlink escapes, and never modifies
input content. Local-file node IDs derive from portable relative paths; URL
nodes derive from canonical URLs.

Adapter contract names are recorded in `metadata.json`. Incremental builds use
`--incremental-from RUN`; the cache fingerprint covers scoring and tokenizer
settings plus the path, byte count, and SHA-256 digest of every input
dependency. SiteProbe, sitemap, CSV, and CMS adapters independently reuse parsed
results when only part of a combined input set changes.

## Commands

| Command | Purpose |
| --- | --- |
| `doctor` | Emit a machine-readable Kujo/runtime/filesystem compatibility report. |
| `build` | Produce a versioned graph and review artifacts. |
| `inspect` | Return one node and all stored relationships. |
| `related` | Rank retained lexical relationships by score. |
| `orphans` | List zero-incoming and weakly connected content. |
| `clusters` | Show deterministic connected topic clusters. |
| `overlaps` | Show high-overlap candidates requiring intent review. |
| `link-opportunities` | Show missing directed-link candidates requiring context review. |
| `analysis` | Show components, centrality, bridge pages, hubs/authorities, depth drift, and cluster health. |
| `explain` | Trace a cluster, overlap, bridge, or link recommendation to bounded measured evidence. |
| `compare` | Compare nodes, fingerprints, clusters, links, and edge weights. |
| `export` | Export graph JSON, standards-compliant GraphML, or bounded SARIF 2.1.0. Existing files require `--force`. |
| `version` | Print version and schema/method contracts. |

Commands return `0` on success and `1` for invalid input, a rejected resource
budget, or an invalid run. The shell launcher returns `2` when Kujo is missing.
Errors are concise, written to stderr, and do not include Python tracebacks.

## Bounded operation

`build` fails closed when a configured bound is exceeded. Important controls:

| Option | Default | Purpose |
| --- | ---: | --- |
| `--max-nodes` | 5,000 | Maximum merged content nodes (hard ceiling: 20,000). |
| `--max-input-bytes` | 512 MiB | Aggregate bytes read from accepted inputs. |
| `--max-candidate-pairs` | 2,000,000 | Sparse similarity work/memory ceiling. |
| `--max-related-per-node` | 20 | Retained nearest relationships per node. |
| `--max-term-document-frequency-ratio` | 1.0 | Ignore terms appearing in a larger fraction of documents. |
| `--max-analysis-items` | 1,000 | Maximum detailed component, cluster-health, and drift entries (totals remain in `analysis.summary`). |
| `--max-output-bytes` | 256 MiB | Complete artifact-set ceiling. |
| `--max-report-tokens` | 2,000 | Declared human-report budget. |
| `--tokenizer-profile` | `deterministic-lexical/v1` | Versioned tokenizer; `unicode-lexical/v1` supports mixed scripts. |
| `--telemetry` | off | Write local timing/resource counters; incompatible with deterministic mode. |

The sparse streaming/top-k scorer holds candidate scores for one source node at
a time and skips pairs with no retained shared term. Candidate pairs can still
grow quadratically for uniformly dense corpora, so the explicit pair ceiling
and document-frequency filter prevent accidental resource exhaustion. Artifacts
are streamed into a private staging directory, validated and budget-checked,
then atomically promoted; a failed gate does not leave a partial run.

## Artifacts and contracts

Each run contains `graph.json`, `nodes.jsonl`, `edges.jsonl`, `clusters.json`,
`overlaps.json`, `orphan-candidates.json`, `link-opportunities.json`,
`analysis.json`, `metadata.json`, `report.md`, `vector-cache.jsonl`,
`adapter-cache.jsonl`, and `manifest.json`; opted-in builds also contain
`telemetry.json`. The vector cache stores normalized terms (never source bodies)
so changed builds can reuse unchanged tokenization. Adapter cache entries contain
normalized parsed corpus data. The manifest
binds every other artifact to a SHA-256 digest. Metadata records configured budgets and actual
input-byte, candidate-pair, and retained-pair usage. Relationships label their
evidence method as `deterministic-lexical/v1`, `existing-internal-link`, or
`measured-provider-evidence`.

JSON Schemas live in `schemas/`. See [methodology](docs/methodology.md),
[agent integration](docs/agent-integration.md), and [security](docs/security.md).

## Determinism and interpretation

`--deterministic` fixes timestamps and run naming so equivalent portable inputs
produce byte-comparable graph artifacts. Topic labels are representative
high-weight terms, not taxonomy decisions. Overlap and link-opportunity outputs
are review queues, never authorization to edit or publish content. Optional
embeddings may enrich future versions but must not replace or relabel lexical
evidence silently.

## Development and verification

```bash
bash scripts/validate.sh
./contentgraph-benchmark --nodes 1000
kujo run scripts/build-demo.kujo
```

Validation checks every Kujo module, runs native adversarial, property,
differential, schema, incremental, adapter, GraphML, and byte-golden tests,
validates JSON schema syntax, and checks patch whitespace. The benchmark corpus
is generated and analyzed by Kujo. See the [interactive demo](demo/index.html),
[demo guide](docs/demo.md), [platform support](docs/platform-support.md),
[telemetry contract](docs/telemetry.md), [upgrade/rollback](docs/upgrade-rollback.md),
and [release qualification](docs/release-qualification-0.3.0.md).
[Contract compatibility](docs/compatibility.md) documents additive v1 evolution
and legacy-run behavior. The [0.3 completion audit](docs/completion-audit-0.3.0.md)
maps every requirement to evidence; the [0.4 review](docs/next-session-review-0.4.md)
contains the next additive opportunity list.

## Enterprise readiness

ContentGraph 0.3 is a native-Kujo, offline, bounded, schema-validated reference
implementation. Tagged releases are validated on Linux, macOS, and Windows,
packaged as checksum-bound platform launch bundles containing the official Kujo
runtime, with Homebrew and Scoop manifests, CycloneDX SBOM, SLSA-shaped
provenance, and GitHub artifact attestations. Synthetic and consented
public-corpus field performance are reported separately.
