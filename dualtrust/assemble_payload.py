#!/usr/bin/env python3
"""Assemble the qualified CC2 Dual Trust payload with a selected public key.

The assembler first reproduces the frozen Neme77 v2 payload with the pinned
Neme77 public key. If that byte-for-byte regression check fails, no Proxima
payload is emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

from keystone import KS_ARCH_ARM, KS_MODE_ARM, Ks

PAYLOAD_ADDRESS = 0x952AC
PAYLOAD_SIZE = 0x318
PEM_SIZE = 451
NEME_PAYLOAD_SHA256 = (
    "33d013ca4a63334fdbbd0adb77bd10f81e2e21c3ac41229e216eb17e5949d06f"
)
NEME_PEM_SHA256 = (
    "b960758986d9daa89d4d61ff96695c0fb6dcaed93025f09f32c595bb05b32e37"
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / "dual_verify.S"
NEME_PUBLIC = ROOT / "vendor" / "neme-v3.7" / "cc2_community_release_public.pem"
SENTINEL = '.incbin "PROXIMA_PUBLIC_KEY.pem"'


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_public_pem(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) != PEM_SIZE:
        raise RuntimeError(f"{path}: expected {PEM_SIZE} bytes, got {len(data)}")
    if not data.startswith(b"-----BEGIN PUBLIC KEY-----\n"):
        raise RuntimeError(f"{path}: expected SubjectPublicKeyInfo PUBLIC KEY PEM")
    if not data.endswith(b"-----END PUBLIC KEY-----\n"):
        raise RuntimeError(f"{path}: malformed PEM footer/newline")
    return data


def prepare_source(pem: bytes) -> str:
    source = SOURCE.read_text(encoding="utf-8")

    # Keystone does not consume the GNU assembler file directives used here.
    cleaned_lines = []
    in_block_comment = False
    for raw in source.splitlines():
        line = raw

        # Strip C-style block comments used only for documentation.
        while True:
            if in_block_comment:
                end = line.find("*/")
                if end < 0:
                    line = ""
                    break
                line = line[end + 2 :]
                in_block_comment = False
                continue

            start = line.find("/*")
            if start < 0:
                break
            end = line.find("*/", start + 2)
            if end >= 0:
                line = line[:start] + line[end + 2 :]
                continue
            line = line[:start]
            in_block_comment = True
            break

        # Strip // comments, matching the upstream assembly process.
        line = line.split("//", 1)[0]
        cleaned_lines.append(line)

    source = "\n".join(cleaned_lines)
    for directive in (
        ".syntax unified",
        ".arm",
        ".section .text",
        ".global dual_verify_wrapper",
    ):
        source = source.replace(directive, "")

    if source.count(SENTINEL) != 1:
        raise RuntimeError("Dual Trust source does not contain exactly one key sentinel")

    byte_directive = ".byte " + ",".join(str(value) for value in pem)
    return source.replace(SENTINEL, byte_directive)


def assemble(pem: bytes) -> bytes:
    source = prepare_source(pem)
    encoded, _ = Ks(KS_ARCH_ARM, KS_MODE_ARM).asm(source, addr=PAYLOAD_ADDRESS)
    payload = bytes(encoded)
    if len(payload) != PAYLOAD_SIZE:
        raise RuntimeError(
            f"Unexpected payload size {len(payload):#x}; expected {PAYLOAD_SIZE:#x}"
        )
    return payload


def regression_self_test() -> None:
    neme_pem = read_public_pem(NEME_PUBLIC)
    if sha256_bytes(neme_pem) != NEME_PEM_SHA256:
        raise RuntimeError("Pinned Neme77 public PEM SHA256 mismatch")

    reference = assemble(neme_pem)
    actual = sha256_bytes(reference)
    if actual != NEME_PAYLOAD_SHA256:
        raise RuntimeError(
            "Neme77 payload regression failed:\n"
            f" expected {NEME_PAYLOAD_SHA256}\n"
            f" actual   {actual}"
        )

    print(f"[OK] Neme77 payload regression: {actual}")


def default_public_key() -> Path:
    config = Path(
        os.environ.get("PROXIMA_CONFIG_DIR", "~/.config/proxima-cc2")
    ).expanduser()
    return config / "proxima_release_public.pem"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-key", type=Path, default=default_public_key())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--self-test-only",
        action="store_true",
        help="only reproduce the frozen Neme77 reference payload",
    )
    args = parser.parse_args()

    regression_self_test()
    if args.self_test_only:
        print("DUAL TRUST REFERENCE: PASS")
        return 0

    public_key = read_public_pem(args.public_key)
    payload = assemble(public_key)
    digest = sha256_bytes(payload)

    if args.output is None:
        raise SystemExit("--output is required unless --self-test-only is used")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)

    print(f"[OK] Proxima public key SHA256: {sha256_bytes(public_key)}")
    print(f"[OK] Proxima payload size: {len(payload)}")
    print(f"[OK] Proxima payload SHA256: {digest}")
    print(f"[OK] Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
