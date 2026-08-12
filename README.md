# ContentGraph

[![Version](https://img.shields.io/badge/version-0.1.0-black)](VERSION)
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

- Python 3.10 or newer for the current compatibility engine.
- A current Kujo runtime. By default the launchers use
  `../kujo/target/release/kujo`; set `KUJO_BIN` to use another binary.
- No third-party Python packages.

```bash
git clone https://github.com/kujolang/contentgraph.git
cd contentgraph
export KUJO_BIN=/absolute/path/to/kujo
./contentgraph doctor
```

The public CLI and benchmark harness are Kujo programs in `src/main.kujo` and
`scripts/benchmark.kujo`. Deterministic parsing and sparse lexical scoring are
currently isolated in `src/contentgraph.py` while those primitives migrate to
Kujo. This boundary is explicit: ContentGraph does not present a Python wrapper
as a native Kujo implementation.

## Quick start

```bash
./contentgraph build --source ./content --out .contentgraph/baseline
./contentgraph orphans .contentgraph/baseline
./contentgraph related .contentgraph/baseline --node guides/getting-started.md
./contentgraph link-opportunities .contentgraph/baseline
./contentgraph export .contentgraph/baseline --format graphml --out graph.graphml
```

Inputs can be repeated and combined:

```bash
./contentgraph build \
  --siteprobe /path/to/.siteprobe/run \
  --source ./docs \
  --searchbridge /path/to/search-performance.json \
  --out .contentgraph/combined
```

Source discovery accepts Markdown, HTML, JSON, and text files, ignores known
generated/dependency directories, rejects symlink escapes, and never modifies
input content. Local-file node IDs derive from portable relative paths; URL
nodes derive from canonical URLs.

## Commands

| Command | Purpose |
| --- | --- |
| `doctor` | Report runtime boundaries and deterministic method. |
| `build` | Produce a versioned graph and review artifacts. |
| `inspect` | Return one node and all stored relationships. |
| `related` | Rank retained lexical relationships by score. |
| `orphans` | List zero-incoming and weakly connected content. |
| `clusters` | Show deterministic connected topic clusters. |
| `overlaps` | Show high-overlap candidates requiring intent review. |
| `link-opportunities` | Show missing directed-link candidates requiring context review. |
| `compare` | Compare nodes, fingerprints, clusters, links, and edge weights. |
| `export` | Export graph JSON or standards-compliant GraphML. Existing files require `--force`. |
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
| `--max-output-bytes` | 256 MiB | Complete artifact-set ceiling. |
| `--max-report-tokens` | 2,000 | Declared human-report budget. |

The sparse inverted index skips document pairs with no shared terms. Candidate
pairs can still grow quadratically for uniformly dense corpora, so the explicit
pair ceiling prevents accidental resource exhaustion. Artifacts are rendered
and budget-checked before a temporary directory is atomically promoted; a
failed budget check does not leave a partial run.

## Artifacts and contracts

Each run contains `graph.json`, `nodes.jsonl`, `edges.jsonl`, `clusters.json`,
`overlaps.json`, `orphan-candidates.json`, `link-opportunities.json`,
`metadata.json`, and `report.md`. Metadata records configured budgets and actual
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
```

Validation compiles the Python engine and Kujo programs, runs adversarial and
deterministic tests through both layers, validates JSON schema syntax, and
checks patch whitespace. The benchmark corpus is generated and orchestrated by
Kujo. See [release qualification](docs/release-qualification-0.1.0.md) and the
[next-session engineering review](docs/next-session-review.md).

## Maturity

The 0.1 line is production-minded and fixture-qualified, but not yet claimed as
enterprise-certified. Native Kujo engine migration, independent large-corpus
profiling, signed release artifacts, and broader interoperability validation
remain explicit next milestones. This honest boundary keeps the project useful
today without overstating operational proof.
