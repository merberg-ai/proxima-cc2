#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${PROXIMA_CONFIG_DIR:-$HOME/.config/proxima-cc2}"
PRIVATE_KEY="$CONFIG_DIR/proxima_release_private.pem"
PUBLIC_KEY="$CONFIG_DIR/proxima_release_public.pem"
VENV="$ROOT/.venv"

echo "============================================================"
echo " Proxima CC2 - build host setup"
echo "============================================================"
echo "Repository : $ROOT"
echo "Config dir : $CONFIG_DIR"
echo

sudo apt-get update
sudo apt-get install -y \
    git \
    openssl \
    python3 \
    python3-venv \
    python3-pip \
    squashfs-tools \
    binutils-arm-linux-gnueabihf \
    jq \
    rsync

if [[ ! -x "$VENV/bin/python" ]]; then
    python3 -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$ROOT/requirements.txt"

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

if [[ -e "$PRIVATE_KEY" && ! -e "$PUBLIC_KEY" ]]; then
    echo "[INFO] deriving missing public key from existing private key"
    openssl pkey -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY"
elif [[ ! -e "$PRIVATE_KEY" && -e "$PUBLIC_KEY" ]]; then
    echo "ERROR: public key exists but private key is missing: $CONFIG_DIR" >&2
    echo "Refusing to generate a new private key beside an unrelated public key." >&2
    exit 1
elif [[ ! -e "$PRIVATE_KEY" && ! -e "$PUBLIC_KEY" ]]; then
    echo "[INFO] generating Proxima RSA-2048 release identity"
    umask 077
    openssl genpkey \
        -algorithm RSA \
        -pkeyopt rsa_keygen_bits:2048 \
        -out "$PRIVATE_KEY"
    openssl pkey -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY"
fi

chmod 600 "$PRIVATE_KEY" "$PUBLIC_KEY"

DERIVED="$(mktemp)"
trap 'rm -f "$DERIVED"' EXIT
openssl pkey -in "$PRIVATE_KEY" -pubout -out "$DERIVED"
if ! cmp -s "$DERIVED" "$PUBLIC_KEY"; then
    echo "ERROR: configured Proxima public/private keys do not match" >&2
    exit 1
fi

PUB_SIZE="$(wc -c < "$PUBLIC_KEY")"
if [[ "$PUB_SIZE" -ne 451 ]]; then
    echo "ERROR: Proxima public PEM must be exactly 451 bytes; got $PUB_SIZE" >&2
    exit 1
fi

mkdir -p "$ROOT/build/dualtrust"
"$VENV/bin/python" "$ROOT/dualtrust/assemble_payload.py" \
    --public-key "$PUBLIC_KEY" \
    --output "$ROOT/build/dualtrust/proxima_dual_verify.bin"

echo
echo "============================================================"
echo " Setup complete"
echo "============================================================"
echo "Private key : $PRIVATE_KEY"
echo "Public key  : $PUBLIC_KEY"
echo
echo "Public key SHA256:"
sha256sum "$PUBLIC_KEY"
echo
echo "No printer was contacted or modified."
echo "Next: ./scripts/preflight.sh"
