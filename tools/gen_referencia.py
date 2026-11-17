#!/usr/bin/env python3
"""La referencia de Fragua en castellano y en inglés, sacada de api/fragua.json (la misma fuente que usarán el
inspector, la ayuda y el autocompletado de Forja):

    python3 tools/gen_referencia.py          # escribe docs/REFERENCIA.md y docs/REFERENCE.en.md
    python3 tools/gen_referencia.py --check  # falla si no están al día
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")

T = {
    "es": {"title": "Referencia de Fragua", "intro": "Sacada de `api/fragua.json` con `tools/gen_referencia.py`: no se edita a mano. "
           "El formato de las escenas está en `docs/ESCENAS.md`.",
           "common": "Propiedades de todos los nodos", "nodes": "Nodos", "behaviors": "Comportamientos listos",
           "actions": "Acciones de los eventos", "functions": "Funciones", "prop": "Propiedad", "type": "Tipo",
           "default": "Por defecto", "range": "Rango", "what": "Qué es", "signals": "Señales", "new": "Se crea con",
           "code": "Código", "example": "Ejemplo",
           "groups": {"tree": "El árbol", "node": "Métodos de Node", "physics": "Física", "world": "El mundo",
                      "input": "Entrada", "game": "Variables del juego", "sound": "Sonido", "effects": "Efectos",
                      "behaviors": "Para comportamientos"}},
    "en": {"title": "Fragua reference", "intro": "Made from `api/fragua.json` by `tools/gen_referencia.py`: do not edit by hand. "
           "The scene format is in `docs/ESCENAS.md` (Spanish).",
           "common": "Properties of every node", "nodes": "Nodes", "behaviors": "Ready-made behaviours",
           "actions": "Event actions", "functions": "Functions", "prop": "Property", "type": "Type",
           "default": "Default", "range": "Range", "what": "What it is", "signals": "Signals", "new": "Made with",
           "code": "Code", "example": "Example",
           "groups": {"tree": "The tree", "node": "Node methods", "physics": "Physics", "world": "The world",
                      "input": "Input", "game": "Game variables", "sound": "Sound", "effects": "Effects",
                      "behaviors": "For behaviours"}},
}


def valor(v):
    if v is None or v == "":
        return "—"
    if isinstance(v, bool):
        return "true" if v else "false"
    return "`%s`" % json.dumps(v, ensure_ascii=False)


def props_tabla(props, l, t):
    if not props:
        return []
    out = ["| %s | %s | %s | %s | %s |" % (t["prop"], t["type"], t["default"], t["range"], t["what"]), "|---|---|---|---|---|"]
    for k, p in props.items():
        rango = ""
        if "min" in p or "max" in p:
            rango = "%s … %s" % (p.get("min", ""), p.get("max", ""))
        out.append("| `%s` | %s | %s | %s | %s |" % (k, p["type"], valor(p.get("default")), rango, p[l]))
    return out + [""]


def generar(api, l):
    t = T[l]
    o = ["# " + t["title"], "", t["intro"], ""]
    o += ["## " + t["functions"], ""]
    grupo = None
    for f in api["functions"]:
        if f["group"] != grupo:
            if grupo is not None:
                o.append("")
            grupo = f["group"]
            o += ["### " + t["groups"].get(grupo, grupo), ""]
        o.append("- `%s`: %s" % (f["sig"], f[l]))
        if f.get("example"):
            o.append("  `%s`" % f["example"])
    o += ["", "## " + t["nodes"], "", "### " + t["common"], ""]
    o += props_tabla(api["common_props"], l, t)
    for nombre, n in api["nodes"].items():
        o += ["### " + nombre, "", n[l], "", "%s: `%s`" % (t["new"], n["new"]), ""]
        o += props_tabla(n["props"], l, t)
        if n["signals"]:
            o += ["%s: %s" % (t["signals"], ", ".join("`%s` (%s)" % (s["name"], s[l]) for s in n["signals"])), ""]
    o += ["## " + t["behaviors"], ""]
    for nombre, b in api["behaviors"].items():
        o += ["### " + nombre, "", b[l], "", "`n.add_behavior(%s())`" % nombre, ""]
        o += props_tabla(b["props"], l, t)
        if b["signals"]:
            o += ["%s: %s" % (t["signals"], ", ".join("`%s` (%s)" % (s["name"], s[l]) for s in b["signals"])), ""]
    o += ["## " + t["actions"], "", "| `do` | %s | %s |" % (t["what"], t["code"]), "|---|---|---|"]
    for nombre, a in api["actions"].items():
        o.append("| `%s` | %s | `%s` |" % (nombre, a[l], a["code"]))
    return "\n".join(o) + "\n"


def main(args):
    api = json.load(open(os.path.join(RAIZ, "api", "fragua.json"), encoding="utf-8"))
    mal = 0
    for l, f in (("es", "REFERENCIA.md"), ("en", "REFERENCE.en.md")):
        ruta = os.path.join(RAIZ, "docs", f)
        texto = generar(api, l)
        if "--check" in args:
            if not os.path.exists(ruta) or open(ruta, encoding="utf-8").read() != texto:
                print("gen_referencia: %s no está al día" % f)
                mal = 1
        else:
            open(ruta, "w", encoding="utf-8").write(texto)
    return mal


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
