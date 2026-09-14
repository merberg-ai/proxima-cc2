# Proxima CC2 architecture

## Scope

Proxima is a custom firmware distribution for the ELEGOO Centauri Carbon 2 (CC2), initially based on official firmware 02.01.00.00.

The first phase is intentionally conservative: establish a reproducible build pipeline, replace the community trust key with a Proxima key, preserve qualified behavior, and keep official ELEGOO firmware acceptance intact.

## Initial firmware composition

```text
Official ELEGOO CC2 02.01.00.00
        |
        +-- boot0            unchanged
        +-- U-Boot           unchanged
        +-- kernel           unchanged
        +-- resource         unchanged
        +-- MCU firmware     unchanged
        +-- rootfs
              |
              +-- root SSH retained
              +-- qualified Z-offset patch retained
              +-- qualified HTTP/WAN patch retained
              +-- qualified upload-while-printing patch retained
              +-- ELEGOO + Proxima Dual Trust
              +-- Proxima release metadata
```

No motion, heater, machine-configuration, or MCU behavior changes belong in the first flashable release.

## Package model

The known CC2 package chain is:

```text
CC2 .zip.sig
  -> ELEG 0x04 signed outer container
      -> ZIP
          -> ota-package-list.json.sig
              -> ELEG 0x83 encrypted/signed manifest
          -> *.swu.sig
              -> ELEG 0x80 encrypted/signed SWU
                  -> CPIO
                      -> sw-description
                      -> resource
                      -> uboot
                      -> boot0
                      -> kernel
                      -> rootfs
                      -> cpio_item_md5
```

Encrypted ELEG payloads use AES-256-CBC. Package signatures use RSA/SHA-256.

## Trust model

### Current qualified Neme77 system

```text
ELEGOO stock signature
        OR
Neme77 community signature
```

### Proxima target

```text
ELEGOO stock signature
        OR
Proxima signature
```

The stock verification path remains intact. Proxima changes only the fallback community public key embedded in the qualified Dual Trust payload.

## One-time trust transition

The current Neme77 updater does not know the Proxima public key. The one-time bootstrap therefore uses the already-qualified root SSH access as a transport mechanism, but the process will be automated and fail-closed.

The bootstrap will:

1. Verify the printer matches the exact known Neme77 v3.7 baseline.
2. Verify firmware/base version and active rootfs.
3. Build the Proxima Dual Trust updater locally.
4. Independently construct the updater by two methods and require byte-for-byte agreement.
5. Upload the candidate to a temporary path.
6. Verify its SHA-256 remotely before installation.
7. Preserve a rollback copy and the immutable `/rom` source remains available.
8. Atomically install the Proxima-trust updater.
9. Reboot.
10. Reconnect and verify the running updater hash.

After this one-time transition, Proxima-signed firmware packages can use the normal firmware update path.

## Build pipeline

```text
stock package
  -> verify frozen stock hash
  -> verify/decode ELEG wrapper
  -> decrypt and verify manifest/SWU
  -> extract CPIO
  -> verify frozen stock components
  -> unsquash rootfs
  -> apply Proxima rootfs changes
  -> rebuild SquashFS
  -> verify rebuilt rootfs contents
  -> rebuild CPIO/SWU metadata
  -> encrypt/sign SWU with Proxima key
  -> create encrypted/signed manifest
  -> create signed outer ELEG package
  -> independently decode and verify produced artifact
  -> emit build manifest + checksums
```

## Key handling

The repository may contain the Proxima **public** signing key. The private key must live outside the repository, planned under:

```text
~/.config/proxima-cc2/proxima_private.pem
```

Recovered device material such as the AES package key must also remain outside the repository.

## Recovery model

Development assumes the operator has:

- Genuine official stock firmware package.
- Verified raw backup of the critical eMMC partitions.
- Known-good Neme77 v3.7 firmware/install material.
- Immutable known-good updater in the installed rootfs `/rom` during the transition phase.

Proxima scripts should never rely on a single recovery mechanism.

## Future layers

After the base firmware/update path is physically qualified, Proxima can grow into distinct layers:

```text
Proxima
  +-- Firmware / updater
  +-- system services
  +-- Web UI
  +-- touchscreen UI
  +-- diagnostics / maintenance
  +-- custom printer commands
  +-- camera / MotionLapse
```

Those features should be developed incrementally rather than bundled into the initial trust/bootstrap milestone.
