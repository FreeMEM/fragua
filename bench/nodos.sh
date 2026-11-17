#!/bin/sh
# bench/nodos.dash a la velocidad real de un A1200 (68020 a 14 MHz, sin memoria Fast) y, con A500=1, de un A500.
# GCC=1: compilado con ./dash --gcc.
#   bench/nodos.sh DASH_DIR
set -e
dash=$(cd "$1" && pwd)
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$aqui/bench" && "$dash/dash" ${GCC:+--gcc} nodos.dash -o "$tmp/Nodos")
maquina=""
[ -z "$A500" ] || maquina="--machine a500"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-400} $maquina --set uae_cpu_speed=real "$tmp/Nodos" 2>&1 | grep -E "bench:|RC=|rror"
