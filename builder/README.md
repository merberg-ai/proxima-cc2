# Builder

This directory will contain the Proxima firmware builder and package-format helpers.

The initial implementation will be derived carefully from the qualified Neme77 v3.7 builder while preserving provenance and GPL licensing.

Planned responsibilities include:

- ELEG parsing and validation.
- AES-256-CBC package decode/encode.
- RSA/SHA-256 signature verification and signing.
- stock package verification.
- CPIO/SWU reconstruction.
- SquashFS extraction/rebuild.
- rootfs patch/overlay application.
- finished-package independent verification.
- build manifest generation.

The builder must reject unexpected stock hashes or package geometry rather than attempting best-effort conversion.
