#!/bin/sh
# Un ejemplo de Fragua en FS-UAE, en modo demo (ENV:FRAGUA_DEMO: juega solo y acaba solo). Enseña su línea de
# medidas.
#
#   tests/juego.sh DASH_DIR examples/plataformas plataformas.dash [segundos-de-captura...]
#
# GCC=1: compilado con ./dash --gcc (si no, con ./dash). REAL=1: la CPU a la velocidad de un A1200 (68020 a
# 14 MHz). A500=1: un A500 (68000 a 7 MHz). Las capturas van a $CAPTURAS (o build/) como <ejemplo>-<s>.png.
# Necesita DASH_KICKSTART (y DASH_KICKSTART_A500 con A500=1).
set -e
dash=$(cd "$1" && pwd); dir=$(cd "$2" && pwd); prog=$3; shift 3
aqui=$(cd "$(dirname "$0")/.." && pwd)
nombre=$(basename "$prog" .dash)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$dir" && "$dash/dash" ${GCC:+--gcc} ${PERFIL:+--profile} ${MEMCHECK:+--memcheck} "$prog" -o "$tmp/Juego" >"$tmp/compilar.txt" 2>&1) || { cat "$tmp/compilar.txt"; exit 1; }
cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys31}" "$tmp/sys"
chmod -R u+w "$tmp/sys"
mkdir -p "$tmp/sys/S"
echo "SetEnv FRAGUA_DEMO 1" >> "$tmp/sys/S/Startup-Extra"
maquina=""
[ -z "$A500" ] || maquina="--machine a500"
caps=${CAPTURAS:-$aqui/build}
mkdir -p "$caps"
shots=""
for s in "$@"; do shots="$shots --screenshot $s $caps/$nombre-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-240} ${KEEP:+--keep $KEEP} $maquina --system "$tmp/sys" --cd "$dir" ${REAL:+--set uae_cpu_speed=real} $shots "$tmp/Juego" 2>&1 | grep -E "$nombre:|RC=|rror|TIMEOUT|FALLO|nil|perfil|memcheck"
