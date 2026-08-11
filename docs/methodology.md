# Deterministic methodology

ContentGraph tokenizes lowercase alphanumeric terms, removes a small versioned
stop-word list, computes document-frequency-smoothed TF-IDF weights, and uses
cosine similarity. Existing internal links form directed graph edges.
Similarity edges are evidence relationships, never rendered as links unless an
authorized operator applies a reviewed recommendation.

- Cluster edges use a configurable similarity threshold (default `0.20`).
- Overlap candidates use a stricter threshold (default `0.55`).
- Link opportunities require meaningful similarity and no existing source-to-target link.
- Orphans have no incoming internal links; weak pages have at most one incoming link.
- Stable IDs hash canonical URL or normalized source path.

This base mode uses no LLM, embedding provider, paid API, or network request.
