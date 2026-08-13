# Deterministic methodology

The default `deterministic-lexical/v1` profile tokenizes lowercase ASCII
alphanumeric terms, removes a small versioned
stop-word list, computes document-frequency-smoothed TF-IDF weights, and uses
cosine similarity. An inverted index computes exact scores only for documents
that share a retained term, while a streaming per-source accumulator feeds
bounded deterministic top-k lists instead of retaining the complete score map.
Existing internal links form directed graph edges.
Similarity edges are evidence relationships, never rendered as links unless an
authorized operator applies a reviewed recommendation.

- Cluster edges use a configurable similarity threshold (default `0.20`).
- Overlap candidates use a stricter threshold (default `0.55`).
- Each node retains its highest-ranked relationships up to
  `--max-related-per-node`; the union of those selections forms the bounded
  lexical edge set.
- Link opportunities are directional and require meaningful retained
  similarity with no existing source-to-target link.
- Orphans have no incoming internal links; weak pages have at most one incoming link.
- Stable IDs hash canonical URL or portable source-relative path.
- `--max-term-document-frequency-ratio` can remove corpus-wide terms before
  candidate generation without changing the evidence-method label.
- `unicode-lexical/v1` uses Unicode letter and number classes for non-English
  and mixed-script corpora. Profiles are explicit in metadata and cache keys;
  changing profiles invalidates token reuse.

`analysis.json` derives undirected components and degree centrality from stored
edges, identifies pages spanning multiple clusters, ranks directed internal-link
hubs and authorities, compares supplied crawl depth with shortest internal-link depth,
and reports per-cluster density/orphan/cross-edge health. The method label is
`deterministic-graph-analysis/v1`.

This base mode uses no LLM, embedding provider, paid API, or network request.

## Explainability and SARIF

`explain --type cluster|overlap|bridge|link --id ID --limit N` returns bounded,
deterministically ordered `contentgraph.explanation/v1` evidence. It contains
measured IDs, scores, and terms and declares `automatic_mutation: false`.

SARIF maps orphans/weak pages to `CG001` warning, potential overlap to `CG002`
warning, and link opportunities to `CG003` note. `--limit` bounds total results
to 1–5,000. Findings require human intent/context review and never authorize
mutation, merge, link, deletion, or publication.
