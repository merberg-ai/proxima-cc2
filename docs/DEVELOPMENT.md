# Development workflow

The canonical Proxima build host is the Ubuntu mini system.

The trust-development pass is intentionally split into host-only work and a
later, separately qualified printer bootstrap. None of the commands in this
document contact the printer.

## First-time setup

```bash
cd ~/src
git clone https://github.com/merberg-ai/proxima-cc2.git
cd proxima-cc2
git checkout dev
./scripts/setup.sh
```

`setup.sh` installs host dependencies, creates `.venv`, and creates the
Proxima RSA-2048 release identity under:

```text
~/.config/proxima-cc2/
  proxima_release_private.pem
  proxima_release_public.pem
```

The private key never belongs in the repository.

## Raw-backup source

By default the tooling uses the newest directory matching:

```text
~/cc2-backup/raw/cc2-raw-backup-*
```

The already-verified raw backup is useful here because it contains both A/B
rootfs partitions. `prepare-baselines.sh` extracts only the updater daemon from
rootfsA/rootfsB and identifies each by frozen SHA-256.

No raw image is modified.

To select a backup explicitly:

```bash
PROXIMA_BACKUP_DIR=~/cc2-backup/raw/cc2-raw-backup-YYYYMMDD-HHMMSS \
  ./scripts/preflight.sh
```

## Preflight

```bash
./scripts/preflight.sh
```

Preflight:

1. verifies the local Proxima private/public keypair,
2. verifies the 451-byte public-PEM geometry required by Dual Trust v2,
3. reproduces the frozen Neme77 payload hash from source,
4. extracts and verifies the frozen stock and Neme77 updater daemons from the
   raw backup,
5. assembles a Proxima-key Dual Trust payload,
6. checks that obvious private/vendor artifacts are not tracked by Git.

## Independent updater construction

```bash
./scripts/build-dualtrust.sh
```

The updater is constructed two ways.

**Method A**

Qualified Neme77 v3.7 daemon -> locate exact embedded Neme77 451-byte public
PEM -> replace only that span with the Proxima 451-byte public PEM.

**Method B**

Frozen stock CC2 02.01.00.00 daemon -> reproduce the Neme77-qualified ARM
verifier with the Proxima public key -> apply the frozen hook/code-cave/ELF
patch geometry.

The build is accepted only when:

```text
Method A == Method B
```

byte-for-byte, and when all bytes outside the embedded public-key span remain
identical to the qualified Neme77 v3.7 daemon.

Successful output:

```text
build/out/proxima-daemon-000
build/out/proxima-daemon-000.sha256
build/dualtrust/manifest.json
```

## What this pass does not do

It does not:

- connect to the printer,
- write the overlay,
- reboot the printer,
- build a complete `.zip.sig` firmware package,
- consume the recovered AES package key,
- change motion/heater/MCU configuration.

Those are subsequent qualification stages.
