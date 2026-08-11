# ContentGraph 0.1.0 release qualification

Status: PASS for the documented deterministic lexical graph contract.

The gate covers path/config fuzzing, malformed HTML/JSON, SiteProbe cyclic-link
inputs, bounded large corpora, explicit node/artifact/report budgets, stale
output rejection, source immutability, optional SearchBridge partial evidence,
offline operation, stable identifiers, and byte-deterministic reruns. Graph
overlaps and opportunities remain review candidates, never authorization to
change or publish content.

Dogfood consumes the validated 60-page SiteProbe run for
`agents.kujolang.ai`; the existing baseline contains 60 nodes, 1,558 edges,
and zero orphan nodes. Run `bash scripts/validate.sh` and
`python3 scripts/benchmark.py --nodes 1000`.

ContentGraph has no network, publish, submit, or ACT command.
