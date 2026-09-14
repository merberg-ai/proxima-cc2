#!/usr/bin/env python3
"""Method B: inject a selected Dual Trust payload into the frozen stock daemon.

This is a Proxima adaptation of Neme77's GPLv3 apply_dualtrust.py. It preserves
the same qualified hook/code-cave/ELF geometry while accepting a caller-supplied
payload. The final daemon hash is intentionally not hard-coded because the
embedded Proxima public key makes it installation-specific until the public key
is frozen in the project.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

STOCK_SHA256 = "b760fd80bb03de28ac348756a9a1c5311066377876570d2fdfd45fb562d91cdb"

HOOK_OFFSET = 0x2C68C
INJECT_OFFSET = 0x852AC
PAYLOAD_SIZE = 0x318

ELF_FILESZ_OFFSET = 0xA4
ELF_MEMSZ_OFFSET = 0xA8
OLD_SEGMENT_SIZE = 0x852AC
NEW_SEGMENT_SIZE = 0x855C4

STOCK_HOOK = bytes.fromhex("4f fb ff eb")
DUAL_HOOK = bytes.fromhex("06 63 01 eb")

RW_MEMSZ_OFFSET = 0xC8
OLD_RW_MEMSZ = 0x1EB0
NEW_RW_MEMSZ = 0x1EF4


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stock_daemon", type=Path)
    parser.add_argument("payload", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    if args.output.exists() or args.output.is_symlink():
        raise RuntimeError(f"Refusing to overwrite existing output: {args.output}")

    actual = sha256_file(args.stock_daemon)
    if actual != STOCK_SHA256:
        raise RuntimeError(
            "Stock daemon SHA256 mismatch:\n"
            f" expected {STOCK_SHA256}\n"
            f" actual   {actual}"
        )

    payload = args.payload.read_bytes()
    if len(payload) != PAYLOAD_SIZE:
        raise RuntimeError(
            f"Unexpected payload size {len(payload):#x}; expected {PAYLOAD_SIZE:#x}"
        )

    data = bytearray(args.stock_daemon.read_bytes())

    if data[HOOK_OFFSET : HOOK_OFFSET + 4] != STOCK_HOOK:
        raise RuntimeError("Original hook instruction mismatch")

    cave = data[INJECT_OFFSET : INJECT_OFFSET + PAYLOAD_SIZE]
    if len(cave) != PAYLOAD_SIZE:
        raise RuntimeError("Injection area extends beyond daemon")
    if any(cave):
        raise RuntimeError("Injection code cave is not empty")

    filesz = int.from_bytes(data[ELF_FILESZ_OFFSET : ELF_FILESZ_OFFSET + 4], "little")
    memsz = int.from_bytes(data[ELF_MEMSZ_OFFSET : ELF_MEMSZ_OFFSET + 4], "little")
    if filesz != OLD_SEGMENT_SIZE:
        raise RuntimeError(f"Unexpected ELF p_filesz: {filesz:#x}")
    if memsz != OLD_SEGMENT_SIZE:
        raise RuntimeError(f"Unexpected ELF p_memsz: {memsz:#x}")

    rw_memsz = int.from_bytes(data[RW_MEMSZ_OFFSET : RW_MEMSZ_OFFSET + 4], "little")
    if rw_memsz != OLD_RW_MEMSZ:
        raise RuntimeError(f"Unexpected RW memory size: {rw_memsz:#x}")

    data[ELF_FILESZ_OFFSET : ELF_FILESZ_OFFSET + 4] = NEW_SEGMENT_SIZE.to_bytes(4, "little")
    data[ELF_MEMSZ_OFFSET : ELF_MEMSZ_OFFSET + 4] = NEW_SEGMENT_SIZE.to_bytes(4, "little")
    data[RW_MEMSZ_OFFSET : RW_MEMSZ_OFFSET + 4] = NEW_RW_MEMSZ.to_bytes(4, "little")
    data[INJECT_OFFSET : INJECT_OFFSET + PAYLOAD_SIZE] = payload
    data[HOOK_OFFSET : HOOK_OFFSET + 4] = DUAL_HOOK

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    shutil.copymode(args.stock_daemon, args.output)

    print("[OK] Frozen stock daemon verified")
    print(f"[OK] Hook offset: {HOOK_OFFSET:#x}")
    print(f"[OK] Injection offset: {INJECT_OFFSET:#x}")
    print(f"[OK] Payload SHA256: {sha256_bytes(payload)}")
    print(f"[OK] Method B daemon SHA256: {sha256_bytes(data)}")
    print(f"[OK] Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
