# Security boundaries

- ContentGraph performs no network requests and never mutates source inputs.
- Source roots and run paths are resolved before reads; symlinked files escaping a supplied root are ignored.
- Discovery excludes `.git`, dependency, generated-output, and private WebOps history directories by default.
- Files are capped at 5 MiB and total input nodes at 20,000.
- Aggregate input bytes, sparse candidate pairs, retained relationships, output
  bytes, and report size are independently bounded.
- SearchBridge inputs are normalized result artifacts, not credential files.
- Large JSON and JSONL artifacts are validated in bounded batches, streamed to
  a private staging directory, hashed, budget-checked, and promoted only as a
  complete new run. Existing output paths are
  rejected, and exports require `--force` before overwriting a file.
- Local node artifacts store portable relative source paths instead of absolute
  workstation paths. Source content is never copied verbatim into reports.
- `vector-cache.jsonl` stores normalized terms, never source bodies. It can
  still reveal topic vocabulary and inherits the run directory's access policy.
- `adapter-cache.jsonl` can contain parsed titles, URLs, and adapter text. Treat
  it as corpus data. Opt-in `telemetry.json` never contains content, URLs, or
  queries and is never transmitted.
- Errors are truncated and normalized; malformed user inputs do not expose a
  traceback through the CLI.
- All accepted structured contracts and every emitted artifact are validated at
  runtime with Kujo's local-only JSON Schema validator. Unknown config keys fail.
- The CLI executes no subprocess during analysis; `doctor` only invokes the
  configured Kujo binary and performs a
  UUID-scoped temporary filesystem check.
- Tagged release archives receive GitHub OIDC artifact attestations and include
  checksums, CycloneDX SBOM, and SLSA-shaped provenance.
- Launchers run Kujo in untrusted mode with only filesystem, process, environment,
  clock, and randomness capabilities needed by the CLI. Network, AI, database,
  and shell execution capabilities remain denied.
