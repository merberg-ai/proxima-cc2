#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_ROOT="${PROXIMA_BACKUP_ROOT:-$HOME/cc2-backup/raw}"
BACKUP_DIR="${PROXIMA_BACKUP_DIR:-}"
OUT="$ROOT/build/baseline"

STOCK_SHA="b760fd80bb03de28ac348756a9a1c5311066377876570d2fdfd45fb562d91cdb"
NEME_SHA="3af6104d0ac76cc043ecf38985e1b00a0d5ceace0a4f4b66820e21f4735a98c7"
REL="opt/inst/daemon-000/daemon-000"

if [[ -z "$BACKUP_DIR" ]]; then
    BACKUP_DIR="$(find "$BACKUP_ROOT" -maxdepth 1 -mindepth 1 \
        -type d -name 'cc2-raw-backup-*' -printf '%T@ %p\n' 2>/dev/null \
        | sort -nr | head -n1 | cut -d' ' -f2- || true)"
fi

if [[ -z "$BACKUP_DIR" || ! -d "$BACKUP_DIR" ]]; then
    echo "ERROR: no CC2 raw backup found under $BACKUP_ROOT" >&2
    echo "Set PROXIMA_BACKUP_DIR=/path/to/cc2-raw-backup-... if needed." >&2
    exit 1
fi

echo "[INFO] using raw backup: $BACKUP_DIR"

if [[ -f "$BACKUP_DIR/SHA256SUMS.portable.txt" ]]; then
    echo "[INFO] verifying portable raw-backup checksums"
    (
        cd "$BACKUP_DIR"
        sha256sum -c SHA256SUMS.portable.txt
    )
fi

mkdir -p "$OUT"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

stock_found=""
neme_found=""

extract_slot() {
    local part="$1"
    local image="$BACKUP_DIR/mmcblk0p${part}.img"
    local target="$TMP/p${part}"

    [[ -f "$image" ]] || return 0
    mkdir -p "$target"

    if ! unsquashfs -d "$target" -no-progress "$image" "$REL" >/dev/null 2>&1; then
        echo "ERROR: could not extract $REL from $image" >&2
        return 1
    fi

    local daemon="$target/$REL"
    [[ -f "$daemon" ]] || {
        echo "ERROR: extraction succeeded but daemon is missing for p${part}" >&2
        return 1
    }

    local digest
    digest="$(sha256sum "$daemon" | awk '{print $1}')"
    echo "[INFO] mmcblk0p${part} daemon: $digest"

    if [[ "$digest" == "$STOCK_SHA" ]]; then
        cp -p "$daemon" "$OUT/stock-daemon-000"
        stock_found="p${part}"
    elif [[ "$digest" == "$NEME_SHA" ]]; then
        cp -p "$daemon" "$OUT/neme-v3.7-daemon-000"
        neme_found="p${part}"
    else
        echo "[WARN] p${part} daemon is neither frozen stock nor qualified Neme77 v3.7"
    fi
}

extract_slot 7
extract_slot 8

if [[ -z "$stock_found" ]]; then
    if [[ -n "${PROXIMA_STOCK_DAEMON:-}" && -f "$PROXIMA_STOCK_DAEMON" ]]; then
        digest="$(sha256sum "$PROXIMA_STOCK_DAEMON" | awk '{print $1}')"
        [[ "$digest" == "$STOCK_SHA" ]] || {
            echo "ERROR: PROXIMA_STOCK_DAEMON has wrong SHA256: $digest" >&2
            exit 1
        }
        cp -p "$PROXIMA_STOCK_DAEMON" "$OUT/stock-daemon-000"
        stock_found="external"
    else
        echo "ERROR: frozen stock daemon was not found in rootfsA/rootfsB." >&2
        echo "Provide PROXIMA_STOCK_DAEMON=/path/to/verified/stock/daemon-000." >&2
        exit 1
    fi
fi

if [[ -z "$neme_found" ]]; then
    if [[ -n "${PROXIMA_NEME_DAEMON:-}" && -f "$PROXIMA_NEME_DAEMON" ]]; then
        digest="$(sha256sum "$PROXIMA_NEME_DAEMON" | awk '{print $1}')"
        [[ "$digest" == "$NEME_SHA" ]] || {
            echo "ERROR: PROXIMA_NEME_DAEMON has wrong SHA256: $digest" >&2
            exit 1
        }
        cp -p "$PROXIMA_NEME_DAEMON" "$OUT/neme-v3.7-daemon-000"
        neme_found="external"
    else
        echo "ERROR: qualified Neme77 v3.7 daemon was not found in rootfsA/rootfsB." >&2
        echo "Provide PROXIMA_NEME_DAEMON=/path/to/verified/neme/daemon-000." >&2
        exit 1
    fi
fi

echo "[OK] stock daemon source: $stock_found"
echo "[OK] Neme77 daemon source: $neme_found"
sha256sum "$OUT/stock-daemon-000" "$OUT/neme-v3.7-daemon-000"
