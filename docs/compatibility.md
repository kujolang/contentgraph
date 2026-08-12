# Contract compatibility policy

ContentGraph uses additive versioning inside the `contentgraph.* /v1` contract
family. Consumers must ignore unknown object properties and new artifact files.
Required fields and evidence-method meanings do not change within v1.

ContentGraph 0.2 reads and queries 0.1 runs that contain the original nine
artifacts. The `analysis` command reports a clear unavailable error for those
runs because `analysis.json` was added in 0.2; rebuilding creates it without
mutating the legacy run. Golden fixtures and the native suite enforce this
backward-read contract.

A future incompatible field removal, type change, or semantic change requires a
new `/v2` schema, explicit migration documentation, and dual-read tests before
release.
