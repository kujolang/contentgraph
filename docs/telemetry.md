# Local telemetry contract

Telemetry is off by default, local only, and requires `build --telemetry`.
ContentGraph writes `telemetry.json` inside the new run and includes its digest
in `manifest.json`. It records elapsed milliseconds, input bytes, output node
count, candidate-pair count, adapter-cache hits, and reused tokenizations.

The v1 schema prohibits source content, URLs, search queries, and network
transmission and rejects undeclared fields. Timing is variable, so `--telemetry`
cannot be combined with `--deterministic`. Nothing uploads this artifact.
