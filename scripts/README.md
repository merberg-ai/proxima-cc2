# Scripts

This directory will contain the operator-facing Proxima tooling.

Planned scripts:

- `setup.sh` - prepare the Ubuntu build host.
- `preflight.sh` - read-only validation of tools, stock firmware, keys, and expected hashes.
- `build.sh` - build a Proxima firmware package.
- `verify.sh` - independently verify a generated package.
- `bootstrap.sh` - one-time automated Neme77 -> Proxima trust transition.
- `rollback-bootstrap.sh` - restore the qualified Neme77 updater if the transition must be reverted.
- `release.sh` - gated release artifact generation.

Scripts that modify a printer must be fail-closed and must verify the exact known baseline before writing anything.
