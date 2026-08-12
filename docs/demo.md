# Public demonstration

The repository ships a non-private three-page corpus in `fixtures/source` and a
checked-in expected run in `fixtures/golden/run`.

```bash
./contentgraph build --source fixtures/source \
  --out .contentgraph/demo --overlap-threshold 0.25 --deterministic
./contentgraph analysis .contentgraph/demo
./contentgraph link-opportunities .contentgraph/demo
```

The expected report shows three content nodes, one lexical edge, two clusters,
three orphan/weak candidates, one overlap candidate, and two directional link
opportunities. The validation suite compares every emitted artifact byte for
byte against the checked-in run.
