# Proxima CC2

**Proxima** is an independent custom firmware project for the ELEGOO Centauri Carbon 2 (CC2).

The project is currently targeting the **02.01.00.00** firmware base and is being developed from a physically qualified Neme77 v3.7 installation. The immediate goal is to establish a reproducible, automated build and trust-transition pipeline on Ubuntu while preserving a reliable path back to stock firmware.

> Proxima is an independent community project and is not affiliated with, endorsed by, or supported by ELEGOO.

## Project goals

- Reproducible firmware builds from a known official CC2 base package.
- Preserve acceptance of official ELEGOO firmware.
- Replace the Neme77 community trust key with a Proxima signing key.
- Automate the one-time Neme77 -> Proxima trust transition.
- Keep recovery and rollback straightforward and verifiable.
- Retain useful qualified Neme77 changes initially: root SSH, GUI Z-offset fix, local HTTP/WAN behavior, and upload-while-printing support.
- Add Proxima-specific services, Web UI, touchscreen UI, diagnostics, custom commands, and improved timelapse features incrementally after the base firmware path is qualified.

## Initial target

The first flashable development release is planned as **Proxima 0.0.1-dev**.

It will intentionally be conservative:

- Base: ELEGOO CC2 02.01.00.00
- Root SSH retained
- Existing qualified Z-offset patch retained
- Existing qualified HTTP/upload patches retained
- Trust changed from `ELEGOO + Neme77` to `ELEGOO + Proxima`
- Proxima release/version markers added
- No changes to motion control, heaters, MCU firmware, boot0, U-Boot, kernel, or printer configuration

## Trust transition

The currently running Neme77 v3.7 updater accepts firmware signed by either the ELEGOO stock key or the Neme77 community key. Proxima will use a one-time automated bootstrap over the existing root SSH access to replace only the embedded community public key in the qualified Dual Trust updater.

After that bootstrap, the printer will accept:

```text
ELEGOO official firmware
        OR
Proxima-signed firmware
```

The first Proxima package can then be installed through the normal firmware-update path. Future Proxima releases will be normal Proxima-signed firmware packages and will not depend on Neme77.

## Build host

The canonical development/build environment is Ubuntu. The planned workflow is:

```text
official 02.01.00.00 firmware package
    -> verify/decode
    -> decrypt manifest + SWU
    -> verify stock components
    -> unpack rootfs
    -> apply Proxima changes
    -> rebuild rootfs/SWU
    -> encrypt/sign with Proxima key
    -> rebuild outer package
    -> independently verify final artifact
```

The eventual developer workflow should be as simple as:

```bash
./scripts/setup.sh
./scripts/preflight.sh
./scripts/build.sh
```

## Repository status

**Early development / bootstrap phase.** No Proxima firmware release is available yet.

The first milestones are:

1. Freeze and document the known-good CC2 02.01.00.00 / Neme77 v3.7 baseline.
2. Build a Proxima RSA signing identity and reproducible Dual Trust payload.
3. Produce two independent constructions of the Proxima updater and require byte-for-byte agreement.
4. Implement the automated reversible Neme77 -> Proxima trust bootstrap.
5. Build and validate Proxima 0.0.1-dev.
6. Perform the first physical flash and post-flash qualification.

## Safety model

Proxima development is deliberately fail-closed. Scripts should verify expected hashes, firmware versions, active rootfs, package structure, and generated artifacts before performing writes. Private signing material and recovered device secrets must never be committed to this repository.

## Credits

Proxima builds on technical findings and GPL-licensed tooling published by the [Centauri Carbon 2 Community](https://github.com/Neme77/centauri-carbon-2-community) project by Neme77, plus official ELEGOO source material and independent reverse engineering.

Detailed attribution and third-party licensing will be maintained as code is imported.
