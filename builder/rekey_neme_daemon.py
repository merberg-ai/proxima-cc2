#!/usr/bin/env python3
"""Method A: replace only the embedded Neme77 public key in the qualified daemon."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

NEME_DAEMON_SHA256 = (
    "3af6104d0ac76cc043ecf38985e1b00a0d5ceace0a4f4b66820e21f4735a98c7"
)
NEME_PEM_SHA256 = (
    "b960758986d9daa89d4d61ff96695c0fb6dcaed93025f09f32c595bb05b32e37"
)
PEM_SIZE = 451

INJECT_OFFSET = 0x852AC
PAYLOAD_SIZE = 0x318
INJECT_END = INJECT_OFFSET + PAYLOAD_SIZE

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NEME_PEM = ROOT / "vendor" / "neme-v3.7" / "cc2_community_release_public.pem"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_pem(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) != PEM_SIZE:
        raise RuntimeError(f"{path}: expected {PEM_SIZE} bytes, got {len(data)}")
    if not data.startswith(b"-----BEGIN PUBLIC KEY-----\n"):
        raise RuntimeError(f"{path}: not a PUBLIC KEY PEM")
    if not data.endswith(b"-----END PUBLIC KEY-----\n"):
        raise RuntimeError(f"{path}: malformed PEM")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("neme_daemon", type=Path)
    parser.add_argument("proxima_public_key", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--neme-public-key", type=Path, default=DEFAULT_NEME_PEM)
    args = parser.parse_args()

    if args.output.exists() or args.output.is_symlink():
        raise RuntimeError(f"Refusing to overwrite existing output: {args.output}")

    actual = sha256_file(args.neme_daemon)
    if actual != NEME_DAEMON_SHA256:
        raise RuntimeError(
            "Neme77 daemon SHA256 mismatch:\n"
            f" expected {NEME_DAEMON_SHA256}\n"
            f" actual   {actual}"
        )

    neme_pem = read_pem(args.neme_public_key)
    if sha256_bytes(neme_pem) != NEME_PEM_SHA256:
        raise RuntimeError("Pinned Neme77 public PEM SHA256 mismatch")

    proxima_pem = read_pem(args.proxima_public_key)
    data = args.neme_daemon.read_bytes()

    count = data.count(neme_pem)
    if count != 1:
        raise RuntimeError(f"Expected one embedded Neme77 PEM, found {count}")

    offset = data.find(neme_pem)
    if not (INJECT_OFFSET <= offset and offset + PEM_SIZE <= INJECT_END):
        raise RuntimeError(
            f"Embedded key at {offset:#x} is outside qualified injected payload "
            f"{INJECT_OFFSET:#x}..{INJECT_END:#x}"
        )

    replaced = data[:offset] + proxima_pem + data[offset + PEM_SIZE :]
    if len(replaced) != len(data):
        raise RuntimeError("Rekey operation changed daemon length")

    if replaced[:offset] != data[:offset] or replaced[offset + PEM_SIZE :] != data[offset + PEM_SIZE :]:
        raise RuntimeError("Unexpected change outside embedded PEM span")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(replaced)
    shutil.copymode(args.neme_daemon, args.output)

    print("[OK] Qualified Neme77 daemon verified")
    print(f"[OK] Embedded Neme77 PEM offset: {offset:#x}")
    print(f"[OK] Proxima public PEM SHA256: {sha256_bytes(proxima_pem)}")
    print(f"[OK] Method A daemon SHA256: {sha256_bytes(replaced)}")
    print(f"[OK] Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
