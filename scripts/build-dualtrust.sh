#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${PROXIMA_CONFIG_DIR:-$HOME/.config/proxima-cc2}"
PUBLIC_KEY="$CONFIG_DIR/proxima_release_public.pem"
VENV="$ROOT/.venv"

BASE="$ROOT/build/baseline"
WORK="$ROOT/build/dualtrust"
OUT="$ROOT/build/out"
NEME_PEM="$ROOT/vendor/neme-v3.7/cc2_community_release_public.pem"

echo "============================================================"
echo " Proxima CC2 - Dual Trust build"
echo "============================================================"

"$ROOT/scripts/preflight.sh"

rm -f \
    "$WORK/proxima-daemon-method-a" \
    "$WORK/proxima-daemon-method-b" \
    "$WORK/manifest.json"

"$VENV/bin/python" "$ROOT/builder/rekey_neme_daemon.py" \
    "$BASE/neme-v3.7-daemon-000" \
    "$PUBLIC_KEY" \
    "$WORK/proxima-daemon-method-a" \
    --neme-public-key "$NEME_PEM"

"$VENV/bin/python" "$ROOT/builder/patch_stock_daemon.py" \
    "$BASE/stock-daemon-000" \
    "$WORK/proxima_dual_verify.bin" \
    "$WORK/proxima-daemon-method-b"

"$VENV/bin/python" "$ROOT/builder/verify_dualtrust_build.py" \
    --method-a "$WORK/proxima-daemon-method-a" \
    --method-b "$WORK/proxima-daemon-method-b" \
    --neme-daemon "$BASE/neme-v3.7-daemon-000" \
    --neme-public-key "$NEME_PEM" \
    --proxima-public-key "$PUBLIC_KEY" \
    --manifest "$WORK/manifest.json"

mkdir -p "$OUT"
cp -p "$WORK/proxima-daemon-method-a" "$OUT/proxima-daemon-000"
sha256sum "$OUT/proxima-daemon-000" > "$OUT/proxima-daemon-000.sha256"

echo
echo "============================================================"
echo " PROXIMA DUAL TRUST BUILD: PASS"
echo "============================================================"
cat "$OUT/proxima-daemon-000.sha256"
echo
echo "Output: $OUT/proxima-daemon-000"
echo "This command does not contact or modify the printer."
