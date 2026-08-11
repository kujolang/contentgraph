# ContentGraph

[![Version](https://img.shields.io/badge/version-0.1.0-black)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![built with Kujo](https://img.shields.io/badge/built%20with-Kujo-white.svg)](https://github.com/kujolang/kujo)

ContentGraph deterministically models how website content relates to other
website content. SiteProbe crawls a site and RAG answers questions over a
corpus; ContentGraph builds the inspectable content network between them.

## Quick start

```bash
./contentgraph doctor
./contentgraph build --siteprobe /path/to/.siteprobe/run --out .contentgraph/baseline
./contentgraph orphans .contentgraph/baseline
./contentgraph related .contentgraph/baseline --node https://example.com/guide
./contentgraph link-opportunities .contentgraph/baseline
```

`build` accepts one or more `--siteprobe`, `--source`, and `--searchbridge`
inputs. Source discovery is bounded to Markdown, HTML, JSON, and text files
under the supplied roots and ignores generated/dependency directories. Every
build has explicit node, artifact-byte, and report-token budgets; stale output
directories are rejected. `--deterministic` produces byte-comparable fixture
runs. All commands are local/offline and source inputs remain read-only.

## Commands

| Command | Purpose |
| --- | --- |
| `doctor` | Confirm local deterministic operation. |
| `build` | Produce nodes, edges, clusters, overlaps, orphans, opportunities, metadata, and report artifacts. |
| `inspect` | Return one node and its relationships. |
| `related` | Rank deterministic lexical relationships. |
| `orphans` | List zero-incoming and weakly connected content. |
| `clusters` | Show connected topic clusters. |
| `overlaps` | Show high-overlap/cannibalization candidates. |
| `link-opportunities` | Show related but unlinked pairs. |
| `compare` | Compare graph additions, removals, cluster, fingerprint, and relationship changes. |
| `export` | Export the versioned graph JSON or GraphML. |
| `version` | Print version and contract. |

## Artifacts

`.contentgraph/<run-id>/` contains `graph.json`, `nodes.jsonl`, `edges.jsonl`,
`clusters.json`, `overlaps.json`, `orphan-candidates.json`,
`link-opportunities.json`, `metadata.json`, and `report.md`. Every relationship
labels its method as `deterministic-lexical/v1` or `existing-internal-link`.

## Maturity boundary

Version 0.1 is fixture-verified for deterministic TF-IDF/cosine relationships,
graph connectivity, source/SiteProbe ingestion, SearchBridge query association,
and comparisons. Topic labels are representative high-weight terms, not human
taxonomy decisions. Overlaps are candidates requiring intent review; they are
not automatic proof of cannibalization. Optional embeddings are an extension
point, not a V1 requirement.

See [methodology](docs/methodology.md), [agent integration](docs/agent-integration.md), and [security](docs/security.md).

## Verification

```bash
bash scripts/validate.sh
python3 scripts/benchmark.py --nodes 1000
```

See [the 0.1.0 release qualification](docs/release-qualification-0.1.0.md).
