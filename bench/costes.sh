#!/bin/sh
# bench/costes.dash a la velocidad de un A1200 (68020 a 14 MHz, sin memoria Fast) y, con A500=1, de un A500.
#
#   bench/costes.sh DASH_DIR
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$aqui/bench" && "$dash/dash" costes.dash -o "$tmp/Costes")
maquina=""
[ -z "$A500" ] || maquina="--machine a500"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-300} $maquina --set uae_cpu_speed=real "$tmp/Costes" 2>&1 | grep -E " ms|RC=|rror|no abre"
