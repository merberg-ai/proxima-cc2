#!/usr/bin/env python3
"""Cross-check the two independent Proxima updater constructions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

NEME_DAEMON_SHA256 = (
    "3af6104d0ac76cc043ecf38985e1b00a0d5ceace0a4f4b66820e21f4735a98c7"
)
PEM_SIZE = 451


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_pem(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) != PEM_SIZE:
        raise RuntimeError(f"{path}: expected {PEM_SIZE} bytes, got {len(data)}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method-a", type=Path, required=True)
    parser.add_argument("--method-b", type=Path, required=True)
    parser.add_argument("--neme-daemon", type=Path, required=True)
    parser.add_argument("--neme-public-key", type=Path, required=True)
    parser.add_argument("--proxima-public-key", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    method_a = args.method_a.read_bytes()
    method_b = args.method_b.read_bytes()
    neme = args.neme_daemon.read_bytes()
    neme_pem = read_pem(args.neme_public_key)
    proxima_pem = read_pem(args.proxima_public_key)

    if sha256_bytes(neme) != NEME_DAEMON_SHA256:
        raise RuntimeError("Neme77 daemon baseline SHA256 mismatch")

    if method_a != method_b:
        mismatch = next(
            (i for i, (left, right) in enumerate(zip(method_a, method_b)) if left != right),
            min(len(method_a), len(method_b)),
        )
        raise RuntimeError(
            "Method A and Method B are not byte-for-byte identical; "
            f"first mismatch at {mismatch:#x}"
        )

    if len(method_a) != len(neme):
        raise RuntimeError("Proxima daemon length differs from Neme77 daemon")

    neme_offsets = []
    start = 0
    while True:
        found = neme.find(neme_pem, start)
        if found < 0:
            break
        neme_offsets.append(found)
        start = found + 1
    if len(neme_offsets) != 1:
        raise RuntimeError(f"Expected one Neme77 PEM in baseline, found {len(neme_offsets)}")

    key_offset = neme_offsets[0]
    if method_a[key_offset : key_offset + PEM_SIZE] != proxima_pem:
        raise RuntimeError("Proxima PEM is not present at the expected embedded-key offset")

    if method_a[:key_offset] != neme[:key_offset]:
        raise RuntimeError("Unexpected changes before embedded public key")
    if method_a[key_offset + PEM_SIZE :] != neme[key_offset + PEM_SIZE :]:
        raise RuntimeError("Unexpected changes after embedded public key")

    changed = sum(left != right for left, right in zip(neme, method_a))
    digest = sha256_bytes(method_a)

    manifest = {
        "schema": 1,
        "result": "PASS",
        "method_a_sha256": digest,
        "method_b_sha256": sha256_bytes(method_b),
        "neme_daemon_sha256": sha256_bytes(neme),
        "proxima_public_pem_sha256": sha256_bytes(proxima_pem),
        "embedded_key_offset": key_offset,
        "embedded_key_size": PEM_SIZE,
        "changed_byte_count_vs_neme": changed,
        "invariant": "All daemon bytes outside the embedded 451-byte public-key span are identical to Neme77 v3.7.",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("[OK] Method A == Method B byte-for-byte")
    print("[OK] Changes are confined to the embedded 451-byte public-key span")
    print(f"[OK] Embedded key offset: {key_offset:#x}")
    print(f"[OK] Changed bytes vs Neme77: {changed}")
    print(f"[OK] Proxima daemon SHA256: {digest}")
    print(f"[OK] Manifest: {args.manifest}")
    print("PROXIMA DUAL TRUST CROSS-CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
