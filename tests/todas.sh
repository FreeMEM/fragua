#!/bin/sh
# Todas las pruebas de Fragua en FS-UAE: Rect, y el Pong en modo demo (500 fotogramas).
#
#   tests/todas.sh DASH_DIR
#
# Necesita DASH_KICKSTART (3.1).
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$aqui/tests" && "$dash/dash" rect.dash -o "$tmp/Rect")
salida=$(cd "$dash" && DASH_EMU_SYS="${DASH_EMU_SYS:-$HOME/.cache/dash-emu/sys31}" python3 tools/emu_run.py --timeout 120 "$tmp/Rect" 2>&1)
echo "$salida" | grep -E "FALLO|TODO BIEN" || echo "FALLO: rect no acaba"
pong=$(sh "$aqui/tests/pong.sh" "$dash" 2>&1)
echo "$pong" | grep "pong:"
if echo "$pong" | grep -q "pong: 500 frames"; then echo "bien: pong"; else echo "FALLO: pong"; fi
