# Scripts

Operator-facing Proxima tooling lives here.

## Implemented on `dev`

- `setup.sh` - prepare the Ubuntu build host, create the Python virtualenv, and create/validate the local Proxima RSA-2048 release identity.
- `prepare-baselines.sh` - read the verified raw A/B backup, extract the updater daemon from each rootfs slot, and identify frozen stock/Neme77 baselines by SHA-256.
- `preflight.sh` - fail-closed host validation; reproduces the frozen Neme77 Dual Trust payload before building the Proxima payload.
- `build-dualtrust.sh` - construct the Proxima updater independently by Method A and Method B and require byte-for-byte equality.

These scripts are host-only and do **not** contact or modify the printer.

## Planned

- `build.sh` - build a complete Proxima firmware package.
- `verify.sh` - independently decode/verify a generated package.
- `bootstrap.sh` - one-time automated Neme77 -> Proxima trust transition.
- `rollback-bootstrap.sh` - restore the qualified Neme77 updater if the transition must be reverted.
- `release.sh` - gated release artifact generation.

Any future script that modifies a printer must be fail-closed and verify the exact known baseline before writing anything.
