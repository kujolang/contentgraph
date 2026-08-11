# Security boundaries

- ContentGraph performs no network requests and never mutates source inputs.
- Source roots and run paths are resolved before reads; symlinked files escaping a supplied root are ignored.
- Discovery excludes `.git`, dependency, generated-output, and private WebOps history directories by default.
- Files are capped at 5 MiB and total input nodes at 20,000.
- SearchBridge inputs are normalized result artifacts, not credential files.
- Output is written only to an explicit/new graph directory; source content is never copied verbatim into reports.
