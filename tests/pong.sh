#!/bin/sh
# El Pong de ejemplo en FS-UAE, en modo demo (ENV:FRAGUA_DEMO: juega solo y acaba a los 500 fotogramas). Enseña el
# marcador y los fotogramas perdidos.
#
#   tests/pong.sh DASH_DIR [captura.png segundos...]
#
# DASH_DIR: un Dash con key_down, bob_paste y bob_width. Necesita DASH_KICKSTART (3.1).
#   REAL=1 tests/pong.sh ...   # la CPU a la velocidad de un A1200 (68020 a 14 MHz)
#   A500=1 tests/pong.sh ...   # un A500 (68000 a 7 MHz), con DASH_KICKSTART_A500
set -e
dash=$1; shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$aqui/examples/pong" && "$dash/dash" pong.dash -o "$tmp/Pong")
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
echo "SetEnv FRAGUA_DEMO 1" >> "$tmp/sys/S/Startup-Extra"
maquina=""
[ -z "$A500" ] || maquina="--machine a500"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-200} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} $shots "$tmp/Pong" 2>&1 | grep -E "pong:|RC=|rror"
