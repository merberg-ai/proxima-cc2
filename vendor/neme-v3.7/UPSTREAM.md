# Neme77 v3.7 upstream provenance

Proxima's initial CC2 trust work is derived from the GPLv3-licensed
`Neme77/centauri-carbon-2-community` project.

This directory pins the exact public upstream material used as the
reference for the first Proxima trust-transition implementation.

## Pinned upstream

- Repository: `https://github.com/Neme77/centauri-carbon-2-community`
- Commit: `3bbbd3e1db0a62d4f2216bad9263257cccebc7e5`
- Snapshot date: 2026-09-13 UTC

Relevant files at that commit:

| Upstream path | Git blob SHA |
| --- | --- |
| `cc2_builder_v3_7/cc2_firmware_builder_v3.7.py` | `7b2902f72fe1b6105f3aa4f1d036b24f85237683` |
| `cc2_builder_v3_7/dualtrust/apply_dualtrust.py` | `1b59b41a21506c3b778f1babcbb97667b69813e8` |
| `cc2_builder_v3_7/dualtrust/assemble_payload.py` | `3edb6262a1875e2f3fee56e01013884511a8b00f` |
| `cc2_builder_v3_7/dualtrust/dual_verify.S` | `698ba5630635c99592794b160c00b74dba492db8` |
| `cc2_builder_v3_7/dualtrust/cc2_community_release_public.pem` | `dd31b85568dcf34de97b76025ef0739cb9e246fa` |

The Neme77 public key is mirrored in this directory because Method A needs
the exact 451-byte PEM that is embedded in the qualified v3.7 updater.

## Frozen CC2 02.01.00.00 hashes

- Stock update daemon:
  `b760fd80bb03de28ac348756a9a1c5311066377876570d2fdfd45fb562d91cdb`
- Neme77 v3.7 Dual Trust daemon:
  `3af6104d0ac76cc043ecf38985e1b00a0d5ceace0a4f4b66820e21f4735a98c7`
- Neme77 Dual Trust payload:
  `33d013ca4a63334fdbbd0adb77bd10f81e2e21c3ac41229e216eb17e5949d06f`
- Neme77 public PEM (raw file SHA-256):
  `b960758986d9daa89d4d61ff96695c0fb6dcaed93025f09f32c595bb05b32e37`

## Deliberately not vendored

No private signing key, AES key, credential, firmware image, extracted
vendor binary, or device backup is stored here.

See the top-level `NOTICE.md` for attribution and licensing context.
