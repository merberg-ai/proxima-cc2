#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${PROXIMA_CONFIG_DIR:-$HOME/.config/proxima-cc2}"
PRIVATE_KEY="$CONFIG_DIR/proxima_release_private.pem"
PUBLIC_KEY="$CONFIG_DIR/proxima_release_public.pem"
VENV="$ROOT/.venv"

required=(git openssl python3 unsquashfs sha256sum cmp)
for tool in "${required[@]}"; do
    command -v "$tool" >/dev/null || {
        echo "ERROR: missing host tool: $tool" >&2
        echo "Run ./scripts/setup.sh first." >&2
        exit 1
    }
done

[[ -x "$VENV/bin/python" ]] || {
    echo "ERROR: missing Proxima virtualenv; run ./scripts/setup.sh" >&2
    exit 1
}

[[ -f "$PRIVATE_KEY" && -f "$PUBLIC_KEY" ]] || {
    echo "ERROR: Proxima release keypair missing from $CONFIG_DIR" >&2
    echo "Run ./scripts/setup.sh first." >&2
    exit 1
}

DERIVED="$(mktemp)"
trap 'rm -f "$DERIVED"' EXIT
openssl pkey -in "$PRIVATE_KEY" -pubout -out "$DERIVED"
cmp -s "$DERIVED" "$PUBLIC_KEY" || {
    echo "ERROR: Proxima public/private keys do not match" >&2
    exit 1
}

PUB_SIZE="$(wc -c < "$PUBLIC_KEY")"
[[ "$PUB_SIZE" -eq 451 ]] || {
    echo "ERROR: Proxima public PEM is $PUB_SIZE bytes; expected 451" >&2
    exit 1
}

NEME_PEM="$ROOT/vendor/neme-v3.7/cc2_community_release_public.pem"
NEME_PEM_SHA="b960758986d9daa89d4d61ff96695c0fb6dcaed93025f09f32c595bb05b32e37"
ACTUAL_NEME_PEM_SHA="$(sha256sum "$NEME_PEM" | awk '{print $1}')"
[[ "$ACTUAL_NEME_PEM_SHA" == "$NEME_PEM_SHA" ]] || {
    echo "ERROR: pinned Neme77 public PEM hash mismatch" >&2
    exit 1
}

echo "[OK] Proxima keypair matches"
echo "[OK] Proxima public PEM is 451 bytes"
echo "[OK] Neme77 public PEM reference is pinned"

"$VENV/bin/python" "$ROOT/dualtrust/assemble_payload.py" --self-test-only

"$ROOT/scripts/prepare-baselines.sh"

mkdir -p "$ROOT/build/dualtrust"
"$VENV/bin/python" "$ROOT/dualtrust/assemble_payload.py" \
    --public-key "$PUBLIC_KEY" \
    --output "$ROOT/build/dualtrust/proxima_dual_verify.bin"

# Guard against accidentally tracking material that should stay private/local.
if git -C "$ROOT" ls-files | grep -E \
    '(^|/)(proxima_release_private\.pem|cc2_aes_key.*|.*\.img|.*\.zip\.sig)$' >/dev/null; then
    echo "ERROR: repository tracks a forbidden private/vendor artifact" >&2
    exit 1
fi

echo
echo "PROXIMA PREFLIGHT: PASS"
echo "No printer was contacted or modified."
