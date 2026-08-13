# Upgrade and rollback

## Upgrade

1. Download the tagged archive, `SHA256SUMS`, SBOM, and provenance attestation.
2. Verify the checksum and GitHub artifact attestation before extraction.
3. Run `./contentgraph doctor`, then rebuild a representative corpus with
   `--deterministic` into a new directory.
4. Compare the old and new runs with `./contentgraph compare OLD NEW`.
5. Promote the new bundle only after expected contract and relationship changes
   are approved. ContentGraph never migrates or mutates an existing run.

## Rollback

Restore the previously verified release archive and keep its existing run
directories. Graph artifacts are immutable, versioned JSON/JSONL, so rollback
does not require a database migration. If a newer graph contract is introduced,
use the older binary with the older run; never rewrite a newer run in place.

ContentGraph 0.3 reads v1 runs produced by 0.1 and 0.2. Exact incremental reuse
from 0.2 synthesizes an empty additive adapter cache when it is absent. The
default tokenizer preserves earlier deterministic lexical behavior.
