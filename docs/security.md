# Security boundaries

- ContentGraph performs no network requests and never mutates source inputs.
- Source roots and run paths are resolved before reads; symlinked files escaping a supplied root are ignored.
- Discovery excludes `.git`, dependency, generated-output, and private WebOps history directories by default.
- Files are capped at 5 MiB and total input nodes at 20,000.
- Aggregate input bytes, sparse candidate pairs, retained relationships, output
  bytes, and report size are independently bounded.
- SearchBridge inputs are normalized result artifacts, not credential files.
- Output is rendered and size-checked in memory, written to a private temporary
  directory, and promoted only as a complete new run. Existing output paths are
  rejected, and exports require `--force` before overwriting a file.
- Local node artifacts store portable relative source paths instead of absolute
  workstation paths. Source content is never copied verbatim into reports.
- Errors are truncated and normalized; malformed user inputs do not expose a
  traceback through the CLI.
