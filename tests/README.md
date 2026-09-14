# Tests

Proxima tests should focus on proving that package generation and trust changes are deterministic and fail closed.

Initial test areas:

- Frozen stock firmware/package hashes.
- ELEG header parsing and signature/hash validation.
- AES round-trip and package geometry.
- manifest-to-SWU linkage.
- stock component hashes after extraction.
- Dual Trust payload size/hash and hook geometry.
- independent Proxima updater constructions are byte-for-byte identical.
- rebuilt rootfs contains only expected first-release changes.
- final firmware package can be independently decoded and verified.
- no private keys, AES keys, raw backups, or vendor firmware are tracked by Git.

Physical printer qualification remains separate from host-side automated tests.
