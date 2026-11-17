#!/usr/bin/env python3
"""Las escenas de Fragua: tools/escena.py genera lo mismo que el .dash que hay al lado de cada .escena de los
ejemplos, y los errores de una escena mal hecha dicen dónde y qué. Acaba con "escenas: bien" o con los fallos."""
import glob
import json
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
ESCENA = os.path.join(AQUI, "..", "tools", "escena.py")
fallos = 0


def mal(msg):
    global fallos
    print("FALLO: " + msg)
    fallos += 1


for ruta in sorted(glob.glob(os.path.join(AQUI, "..", "examples", "*", "*.escena")) + glob.glob(os.path.join(AQUI, "..", "plantilla", "*", "*.escena"))):
    gen = subprocess.run([sys.executable, ESCENA, "--stdout", ruta], capture_output=True, text=True)
    hay = open(os.path.splitext(ruta)[0] + ".dash", encoding="utf-8").read()
    if gen.returncode != 0 or gen.stdout != hay:
        mal("%s: el .dash no es el que genera la escena (python3 tools/escena.py %s)" % (os.path.basename(ruta), ruta))

MALAS = [
    ({"name": "X", "root": {"type": "Node", "name": "X"}}, "falta \"fragua\": 1"),
    ({"fragua": 1, "name": "X", "root": {"type": "Sprit2D", "name": "S"}}, "el tipo 'Sprit2D' no existe"),
    ({"fragua": 1, "name": "X", "root": {"type": "Node2D", "name": "N", "props": {"colour": 3}}}, "no tiene la propiedad 'colour'"),
    ({"fragua": 1, "name": "X", "root": {"type": "Body2D", "name": "B", "behaviors": [{"type": "Platformer", "props": {"sped": 2}}]}}, "Platformer no tiene la propiedad 'sped'"),
    ({"fragua": 1, "name": "X", "root": {"type": "Sprite2D", "name": "S"}}, "necesita \"image\""),
    ({"fragua": 1, "name": "X", "root": {"type": "Node", "name": "N", "events": [{"signal": "x", "actions": [{"do": "explode"}]}]}}, "la acción 'explode' no existe"),
    ({"fragua": 1, "name": "X", "root": {"type": "Node2D", "name": "N", "props": {"x": "diez"}}}, "se esperaba un número entero"),
]
with tempfile.TemporaryDirectory() as d:
    for i, (escena, esperado) in enumerate(MALAS):
        ruta = os.path.join(d, "mala%d.escena" % i)
        json.dump(escena, open(ruta, "w"))
        r = subprocess.run([sys.executable, ESCENA, "--check", ruta], capture_output=True, text=True)
        if esperado is None:
            continue
        if r.returncode == 0 or esperado not in r.stderr:
            mal("mala%d: se esperaba un error con %r y salió %r" % (i, esperado, r.stderr.strip()))

# Each property of a behaviour in api/fragua.json is a field of its struct in src/behaviors.dash
api = json.load(open(os.path.join(AQUI, "..", "api", "fragua.json"), encoding="utf-8"))
fuente = open(os.path.join(AQUI, "..", "src", "behaviors.dash"), encoding="utf-8").read()
for nombre, b in api["behaviors"].items():
    i = fuente.find("struct %s: Script" % nombre)
    if i < 0:
        mal("el comportamiento %s no está en src/behaviors.dash" % nombre)
        continue
    cuerpo = fuente[i:fuente.find("\nend\n", i)]
    for p in b["props"]:
        if "\n    %s: " % p not in cuerpo:
            mal("%s.%s está en api/fragua.json pero no en el struct" % (nombre, p))
r = subprocess.run([sys.executable, os.path.join(AQUI, "..", "tools", "gen_referencia.py"), "--check"], capture_output=True, text=True)
if r.returncode != 0:
    mal(r.stdout.strip() + " (python3 tools/gen_referencia.py)")

print("escenas: bien" if fallos == 0 else "escenas: %d fallos" % fallos)
sys.exit(1 if fallos else 0)
