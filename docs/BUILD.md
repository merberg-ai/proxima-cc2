# Build and development workflow

## Canonical build host

The primary development machine is an Ubuntu system. The expected checkout location is:

```text
~/src/proxima-cc2
```

Private build configuration is expected under:

```text
~/.config/proxima-cc2/
```

Verified recovery backups remain outside the repository, for example:

```text
~/cc2-backup/
```

The raw eMMC backup is recovery material only and must not be used as the normal firmware build source.

## Normal build source

Every normal Proxima build should begin from the same known official ELEGOO 02.01.00.00 firmware package and verify its frozen SHA-256 before decoding it.

This keeps builds reproducible and prevents live printer state from leaking into firmware artifacts.

## Planned commands

```bash
./scripts/setup.sh
./scripts/preflight.sh
./scripts/build.sh
./scripts/verify.sh build/out/PROXIMA_CC2_0.0.1-dev.zip.sig
```

### setup.sh

One-time host setup. Planned responsibilities:

- Install host dependencies.
- Create a Python virtual environment.
- Install Python build dependencies such as Keystone.
- Verify ARM binutils and SquashFS tooling.
- Create the private configuration directory.
- Generate a Proxima RSA keypair if one does not already exist.
- Locate and validate required private inputs without committing them.

### preflight.sh

Read-only validation. It should verify all inputs and tooling and make no firmware changes.

### build.sh

Produce a complete Proxima firmware artifact from the frozen stock package.

### verify.sh

Independently reopen the produced package, validate the ELEG structure, signatures, encryption geometry, manifest links, rootfs contents, and expected hashes.

## Planned private files

```text
~/.config/proxima-cc2/
  proxima_private.pem
  proxima_public.pem
  cc2_aes_key_v1.bin
  build.env
```

The public key may also be copied into the repository where needed for the embedded verifier. The private key and AES key must never be committed.

## Planned build output

```text
build/out/
  PROXIMA_CC2_0.0.1-dev.zip.sig
  PROXIMA_CC2_0.0.1-dev.zip.sig.sha256
  build-manifest.json
  build.log
```

The build manifest should identify the Proxima version, ELEGOO base version, source Git commit, stock firmware hash, generated rootfs hash, final package hash, and signing public-key fingerprint.

## Release policy

A development build is not a release. A future release command should refuse to produce release artifacts unless:

- the Git tree is clean;
- the version is not marked `-dev`;
- tests pass;
- stock inputs match frozen hashes;
- the finished package passes independent verification;
- no private material is staged or tracked.
