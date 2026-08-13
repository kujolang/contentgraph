# Agent integration

Internal Link Specialists should consume `link-opportunities.json` and inspect
context before proposing links. Cannibalization Analysts should treat
`overlaps.json` as candidate evidence and add measured query/page evidence when
available. Information Architecture Auditors should use directed link edges,
depth, cluster membership, and orphan/weak status. Portfolio agents may combine
graph evidence with SearchBridge measurements but must keep recommendation,
action, and outcome separate.

Agents should call `explain` with a small explicit limit before presenting a
cluster, overlap, bridge, or link conclusion. The returned schema is bounded and
declares that it cannot authorize automatic mutation. SARIF is a CI review queue
with the same restriction; severity is triage priority, not editorial truth.
