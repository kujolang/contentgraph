# Examples

```bash
./contentgraph build --source fixtures/source --out .contentgraph/example
./contentgraph inspect .contentgraph/example --node guide-a.md
./contentgraph export .contentgraph/example --format graphml --out .contentgraph/example/graph.graphml
```

Use `--siteprobe` to retain canonical URLs, links, crawl depth, fingerprints,
and sitemap membership from a validated SiteProbe run.
