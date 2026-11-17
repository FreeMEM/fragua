#!/bin/sh
# Todas las pruebas de Fragua en FS-UAE, por los dos caminos de Dash (./dash y ./dash --gcc) y en las dos máquinas
# (A1200 y, con A500=1, también A500):
#   - Rect y el árbol de nodos (rect.dash, nodos.dash): acaban con "TODO BIEN";
#   - las escenas: tools/escena.py genera lo mismo que hay en el repo, y sus errores se entienden;
#   - los ejemplos en modo demo (juegan solos): el Pong de la capa 1, el Pong con nodos, plataformas e isométrico.
#
#   tests/todas.sh DASH_DIR            # A1200
#   A500=1 tests/todas.sh DASH_DIR     # A1200 y A500
#
# Necesita DASH_KICKSTART (y DASH_KICKSTART_A500). Acaba con "fallos: N".
dash=$(cd "$1" && pwd)
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fallos=0
mal() { echo "FALLO: $*"; fallos=$((fallos + 1)); }

python3 "$aqui/tests/escenas.py" || mal "escenas"

maquinas="a1200"
[ -z "$A500" ] || maquinas="a1200 a500"
for maq in $maquinas; do
    for camino in directo gcc; do
        opt=""
        [ $camino = gcc ] && opt="--gcc"
        m=""
        [ $maq = a500 ] && m="--machine a500"
        for p in rect nodos; do
            (cd "$aqui/tests" && "$dash/dash" $opt $p.dash -o "$tmp/$p" >"$tmp/c.txt" 2>&1) || { cat "$tmp/c.txt"; mal "$p no compila ($camino)"; continue; }
            sal=$(cd "$dash" && DASH_EMU_SYS="${DASH_EMU_SYS:-$HOME/.cache/dash-emu/sys31}" python3 tools/emu_run.py --timeout 150 $m "$tmp/$p" 2>&1)
            if echo "$sal" | grep -q "TODO BIEN"; then echo "bien: $p ($maq, $camino)"; else echo "$sal" | grep -E "FALLO|RC=|rror"; mal "$p ($maq, $camino)"; fi
        done
        export GCC=""
        [ $camino = gcc ] && export GCC=1
        export A500=""
        [ $maq = a500 ] && export A500=1
        for e in "pong pong.dash pong: 500 frames" "pong_nodos pong_nodos.dash pong_nodos: 500 frames" \
                 "plataformas plataformas.dash plataformas: 60[01] frames" "iso iso.dash iso: "; do
            set -- $e
            dir=$1; prog=$2; shift 2; esperado="$*"
            sal=$(TIEMPO=300 sh "$aqui/tests/juego.sh" "$dash" "$aqui/examples/$dir" "$prog" 2>&1)
            linea=$(echo "$sal" | grep -E "^[a-z_]+: [0-9]+ frames")
            if echo "$linea" | grep -qE "$esperado"; then echo "bien: $linea ($maq, $camino)"; else echo "$sal" | tail -3; mal "$dir ($maq, $camino)"; fi
        done
    done
done
echo "fallos: $fallos"
[ $fallos -eq 0 ]
