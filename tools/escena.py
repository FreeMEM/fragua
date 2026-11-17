#!/usr/bin/env python3
"""Convierte una escena de Fragua (.escena, JSON) en un .dash que la monta: lo que hará el editor de escenas de Forja
al guardar (forma B del diseño). El formato está en docs/ESCENAS.md; los tipos de las propiedades, en
api/fragua.json.

    python3 tools/escena.py enemigo.escena [más.escena ...]   # escribe enemigo.dash al lado de cada una
    python3 tools/escena.py --stdout enemigo.escena           # lo enseña sin escribirlo
    python3 tools/escena.py --check enemigo.escena            # solo comprueba la escena

Los errores dicen el fichero, la ruta del nodo y qué falta, en castellano.
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
API = json.load(open(os.path.join(AQUI, "..", "api", "fragua.json"), encoding="utf-8"))


class ErrorEscena(Exception):
    pass


def nombre_funcion(nombre):
    return "scene_" + re.sub(r"[^a-z0-9]+", "_", nombre.lower()).strip("_")


def nombre_struct(*trozos):
    return "".join(re.sub(r"[^A-Za-z0-9]", "", t[:1].upper() + t[1:]) for t in trozos)


def dash_texto(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def dash_valor(tipo, v):
    if tipo == "Fixed":
        if isinstance(v, int) or (isinstance(v, float) and v.is_integer()):
            return "Fixed(%d)" % int(v)
        return "Fixed(%s)" % repr(float(v))
    if tipo == "Bool":
        return "true" if v else "false"
    if tipo in ("Int", "Color"):
        if not isinstance(v, int) or isinstance(v, bool):
            raise ErrorEscena("se esperaba un número entero y hay %r" % (v,))
        return str(v)
    return dash_texto(v)


class Generador:
    def __init__(self, ruta):
        self.ruta = ruta
        self.dir = os.path.dirname(os.path.abspath(ruta))
        try:
            self.escena = json.load(open(ruta, encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ErrorEscena("%s: no es JSON válido (línea %d: %s)" % (ruta, e.lineno, e.msg))
        if self.escena.get("fragua") != 1:
            raise ErrorEscena("%s: falta \"fragua\": 1 (la versión del formato)" % ruta)
        if "name" not in self.escena or "root" not in self.escena:
            raise ErrorEscena("%s: una escena necesita \"name\" y \"root\"" % ruta)
        self.nombre = self.escena["name"]
        self.lineas = []
        self.structs = []
        self.imports = []
        self.cuenta = 0
        self.rutas = {}            # ruta en la escena -> variable

    def error(self, donde, msg):
        raise ErrorEscena("%s, nodo %s: %s" % (self.ruta, donde or ".", msg))

    def var(self):
        self.cuenta += 1
        return "n%d" % self.cuenta

    def linea(self, s):
        self.lineas.append("    " + s)

    def props_comunes(self, v, props, donde):
        for k, val in props.items():
            if k in ("x", "y"):
                continue
            p = API["common_props"].get(k)
            if p is None:
                continue
            self.poner(v, p, val, donde, k)

    def poner(self, v, p, val, donde, k):
        try:
            valor = dash_valor(p["type"], val)
        except ErrorEscena as e:
            self.error(donde, "la propiedad %s: %s" % (k, e))
        dest = p["set"].replace("n.", v + ".", 1)
        if "(V)" in dest:
            self.linea(dest.replace("(V)", "(%s)" % valor))
        else:
            self.linea("%s = %s" % (dest, valor))

    def nodo(self, d, donde, padre=None):
        tipo = d.get("type")
        nombre = d.get("name")
        if not nombre:
            self.error(donde, "le falta \"name\"")
        donde = nombre if donde is None else donde + "/" + nombre
        props = d.get("props", {})
        x, y = props.get("x", 0), props.get("y", 0)
        v = self.var()
        n = dash_texto(nombre)
        if tipo == "Instance":
            escena = d.get("scene")
            if not escena:
                self.error(donde, "una Instance necesita \"scene\" (el fichero .escena)")
            otra = Generador(os.path.join(self.dir, escena))
            self.importar(escena)
            self.linea("%s = %s()" % (v, nombre_funcion(otra.nombre)))
            self.linea("%s.name = %s" % (v, n))
            if x or y:
                self.linea("%s.set_pos(%d, %d)" % (v, x, y))
            self.props_comunes(v, props, donde)
        else:
            info = API["nodes"].get(tipo)
            if info is None:
                self.error(donde, "el tipo %r no existe; los que hay: %s, Instance" % (tipo, ", ".join(API["nodes"])))
            for k in props:
                if k not in info["props"] and k not in API["common_props"] and not (tipo == "StaticBody2D" and k == "mask"):
                    self.error(donde, "%s no tiene la propiedad %r; tiene: %s" % (tipo, k, ", ".join(list(info["props"]) + list(API["common_props"]))))
            self.crear(v, tipo, n, x, y, props, donde)
            self.props_comunes(v, props, donde)
            for k, p in info["props"].items():
                if k in props and "set" in p:
                    self.poner(v, p, props[k], donde, k)
        for g in d.get("groups", []):
            self.linea("%s.add_to_group(%s)" % (v, dash_texto(g)))
        if d.get("script"):
            self.linea("%s.script = %s()" % (v, d["script"]))
        for i, b in enumerate(d.get("behaviors", [])):
            self.comportamiento(v, b, donde)
        if d.get("events"):
            self.eventos(v, d["events"], donde)
        ruta_rel = donde.split("/", 1)[1] if "/" in donde else "."
        self.rutas[ruta_rel] = v
        if padre is not None:
            self.linea("%s.add_child(%s)" % (padre, v))
        for h in d.get("children", []):
            self.nodo(h, donde, v)
        if tipo == "TileMap" and props.get("spawn"):
            self.spawn(v, props["spawn"], donde, padre)
        return v

    def importar(self, escena):
        dash = os.path.splitext(escena)[0] + ".dash"
        if dash not in self.imports:
            self.imports.append(dash)

    def crear(self, v, tipo, n, x, y, props, donde):
        L = self.linea
        if tipo == "Node":
            L("%s = new_node(%s)" % (v, n))
            if x or y:
                L("%s.set_pos(%d, %d)" % (v, x, y))
        elif tipo == "Node2D":
            L("%s = new_node2d(%s, %d, %d)" % (v, n, x, y))
        elif tipo in ("Sprite2D", "AnimatedSprite2D"):
            if not props.get("image"):
                self.error(donde, "un %s necesita \"image\" (un IFF)" % tipo)
            f = "new_sprite2d" if tipo == "Sprite2D" else "new_animated_sprite2d"
            L("%s = %s(%s, image_cached(%s), %d, %d)" % (v, f, n, dash_texto(props["image"]), x, y))
            if props.get("offset"):
                ox, oy = props["offset"]
                L("%s.sprite.ox = %d" % (v, ox))
                L("%s.sprite.oy = %d" % (v, oy))
            for an, a in props.get("animations", {}).items():
                fr = a.get("frames")
                if not fr:
                    self.error(donde, "la animación %r no tiene \"frames\"" % an)
                L("add_animation(%s, %s, [%s], %d, %s)" % (v, dash_texto(an), ", ".join(str(int(f)) for f in fr),
                                                           int(a.get("speed", 6)), "true" if a.get("loop", True) else "false"))
            if props.get("autoplay"):
                if props["autoplay"] not in props.get("animations", {}):
                    self.error(donde, "autoplay %r no es ninguna de sus animaciones" % props["autoplay"])
                L("%s.play(%s)" % (v, dash_texto(props["autoplay"])))
        elif tipo == "HardwareSprite2D":
            L("%s = new_hw_sprite2d(%s, %s, %d, %d)" % (v, n, dash_texto(props.get("image", "")), x, y))
        elif tipo == "CollisionShape2D":
            if "circle" in props:
                cx, cy, r = props["circle"]
                L("%s = new_shape_circle(%s, %d, %d, %d)" % (v, n, cx, cy, r))
            else:
                rx, ry, rw, rh = props.get("rect", [0, 0, 16, 16])
                L("%s = new_shape_rect(%s, %d, %d, %d, %d)" % (v, n, rx, ry, rw, rh))
        elif tipo == "Body2D":
            L("%s = new_body2d(%s, %d, %d)" % (v, n, x, y))
        elif tipo == "StaticBody2D":
            L("%s = new_static_body2d(%s, %d, %d)" % (v, n, x, y))
        elif tipo == "Area2D":
            L("%s = new_area2d(%s, %d, %d)" % (v, n, x, y))
        elif tipo == "TileMap":
            if not props.get("file"):
                self.error(donde, "un TileMap necesita \"file\" (un .fmap)")
            if props.get("tileset"):
                L("%s = new_tilemap_with(%s, %s, %s)" % (v, n, dash_texto(props["file"]), dash_texto(props["tileset"])))
            else:
                L("%s = new_tilemap(%s, %s)" % (v, n, dash_texto(props["file"])))
            L("if %s == nil" % v)
            L("    Print %s" % dash_texto("Fragua: the map %s (or its tileset) does not load" % props["file"]))
            L("    return n1")
            L("end")
            if x or y:
                L("%s.set_pos(%d, %d)" % (v, x, y))
        elif tipo == "Camera2D":
            L("%s = new_camera2d(%s)" % (v, n))
            self.camara = (v, props)
        elif tipo == "Label":
            L("%s = new_label(%s, %d, %d, %s, %d, %d)" % (v, n, x, y, dash_texto(props.get("text", "")), props.get("pen", 1), props.get("bg", 0)))
        elif tipo == "Timer":
            L("%s = new_timer(%s, %d, %s)" % (v, n, props.get("wait", 50), "true" if props.get("one_shot") else "false"))
        elif tipo == "AudioPlayer":
            L("%s = new_audio(%s, %s, %d)" % (v, n, dash_texto(props.get("file", "")), props.get("channel", -1)))
        elif tipo == "Particles2D":
            L("%s = new_particles2d(%s, %d, %d, %d, %d)" % (v, n, x, y, props.get("amount", 8), props.get("pen", 1)))

    def comportamiento(self, v, b, donde):
        tipo = b.get("type")
        info = API["behaviors"].get(tipo)
        if info is None:
            self.error(donde, "el comportamiento %r no existe; los que hay: %s" % (tipo, ", ".join(API["behaviors"])))
        bv = "b" + self.var()[1:]
        self.linea("%s = %s()" % (bv, tipo))
        for k, val in b.get("props", {}).items():
            p = info["props"].get(k)
            if p is None:
                self.error(donde, "%s no tiene la propiedad %r; tiene: %s" % (tipo, k, ", ".join(info["props"])))
            self.poner(bv, dict(p, set="n." + k), val, donde, k)
        self.linea("%s.add_behavior(%s)" % (v, bv))

    def spawn(self, mapa, spawn, donde, padre):
        dest = padre or mapa
        for clase, escena in spawn.items():
            otra = Generador(os.path.join(self.dir, escena))
            self.importar(escena)
            self.linea("for o in map_objects(%s, %s)" % (mapa, dash_texto(clase)))
            self.linea("    s = %s()" % nombre_funcion(otra.nombre))
            self.linea("    s.set_pos(map_object_x(%s, o), map_object_y(%s, o))" % (mapa, mapa))
            self.linea("    %s.add_child(s)" % dest)
            self.linea("end")

    # --- eventos con acciones ---

    def eventos(self, v, eventos, donde):
        nodo = donde.rsplit("/", 1)[-1]
        nombre = nombre_struct(self.nombre, "Events") if nodo == self.nombre else nombre_struct(self.nombre, nodo, "Events")
        if any(s.startswith("struct %s:" % nombre) for s in self.structs):
            nombre += str(self.cuenta)
        cuerpo = []
        for e in eventos:
            sig = e.get("signal")
            if not sig:
                self.error(donde, "un evento necesita \"signal\"")
            cond = ["name == %s" % dash_texto(sig)]
            if e.get("if_group"):
                cond.append("other != nil and other.is_in_group(%s)" % dash_texto(e["if_group"]))
            if e.get("if"):
                cond.append("(%s)" % e["if"])
            cuerpo.append("        if " + " and ".join(cond))
            for a in e.get("actions", []):
                for l in self.accion(a, donde):
                    cuerpo.append("            " + l)
            cuerpo.append("            self.fired = self.fired + 1")
            cuerpo.append("        end")
        s = ["# The events of %s in the scene %s" % (nodo, self.nombre),
             "struct %s: Script" % nombre,
             "    fired: Int = 0                # events that happened",
             "",
             "    func ready(n: Node)", "    end", "",
             "    func process(n: Node, delta: Int)", "    end", "",
             "    func physics_process(n: Node)", "    end", "",
             "    func on_signal(n: Node, name: String, from: Node, data: Int)",
             "        other = node_by_id(data)"] + cuerpo + ["    end", "end"]
        self.structs.append("\n".join(s))
        self.linea("%s.add_behavior(%s())" % (v, nombre))

    def accion(self, a, donde):
        do = a.get("do")
        if do not in API["actions"]:
            self.error(donde, "la acción %r no existe; las que hay: %s" % (do, ", ".join(API["actions"])))
        objetivo = "n"
        if a.get("target") == "other":
            objetivo = "other"
        elif a.get("target"):
            objetivo = "n.get_node(%s)" % dash_texto(a["target"])
        if do == "add":
            return ["game_add(%s, %d)" % (dash_texto(a["var"]), a.get("value", 1))]
        if do == "set":
            return ["game_set(%s, %d)" % (dash_texto(a["var"]), a.get("value", 0))]
        if do == "sound":
            return ["play_sound(%s)" % dash_texto(a["file"])]
        if do == "music":
            return ["play_music(%s)" % dash_texto(a["file"])]
        if do == "destroy":
            if objetivo == "other":
                return ["if other != nil", "    other.queue_free()", "end"]
            return ["%s.queue_free()" % objetivo]
        if do == "emit":
            return ["n.emit(%s, %d)" % (dash_texto(a["signal"]), a.get("data", 0))]
        if do == "damage":
            return ["send_signal(other, \"damage\", n, %d)" % a.get("value", 1)]
        if do == "spawn":
            otra = Generador(os.path.join(self.dir, a["scene"]))
            self.importar(a["scene"])
            return ["spawn(n, %s(), %d, %d)" % (nombre_funcion(otra.nombre), a.get("x", 0), a.get("y", 0))]
        if do == "play":
            return ["%s.play(%s)" % (objetivo, dash_texto(a["anim"]))]
        if do == "start":
            return ["%s.start()" % objetivo]
        if do in ("show", "hide"):
            return ["%s.visible = %s" % (objetivo, "true" if do == "show" else "false")]
        if do == "change_scene":
            otra = Generador(os.path.join(self.dir, a["scene"]))
            self.importar(a["scene"])
            return ["change_scene(%s())" % nombre_funcion(otra.nombre)]
        if do == "quit":
            return ["quit()"]
        if do == "code":
            return a.get("dash", "").splitlines()
        return []

    def generar(self):
        self.camara = None
        raiz = self.nodo(self.escena["root"], None)
        if self.camara:
            v, props = self.camara
            if props.get("target"):
                t = props["target"]
                self.linea("%s.camera.target = %s.get_node(%s)" % (v, raiz, dash_texto(t)))
            lim = props.get("limits", "map")
            if lim == "map":
                self.linea("if fragua_first_map(%s) != nil" % raiz)
                self.linea("    %s.camera.limit_w = map_pixel_width(fragua_first_map(%s))" % (v, raiz))
                self.linea("    %s.camera.limit_h = map_pixel_height(fragua_first_map(%s))" % (v, raiz))
                self.linea("end")
            elif lim:
                self.linea("%s.camera.limit_w = %d" % (v, lim[0]))
                self.linea("%s.camera.limit_h = %d" % (v, lim[1]))
        for c in self.escena.get("connections", []):
            for k in ("from", "signal", "to"):
                if k not in c:
                    raise ErrorEscena("%s: una conexión necesita \"from\", \"signal\" y \"to\"" % self.ruta)
            de = self.rutas.get(c["from"])
            a = self.rutas.get(c["to"])
            if de is None or a is None:
                raise ErrorEscena("%s: la conexión %s -> %s: no hay nodo %r" % (self.ruta, c["from"], c["to"], c["from"] if de is None else c["to"]))
            self.linea("%s.connect(%s, %s)" % (de, dash_texto(c["signal"]), a))
        self.linea("return %s" % raiz)
        base = os.path.basename(self.ruta)
        sal = ["# Generated by Fragua (tools/escena.py) from %s: edit the scene, not this file." % base, ""]
        sal += ['import "%s"' % i for i in self.imports]
        if self.imports:
            sal.append("")
        for s in self.structs:
            sal += [s, ""]
        sal.append("# The scene %s: a new tree each call" % self.nombre)
        sal.append("func %s() -> Node" % nombre_funcion(self.nombre))
        sal += self.lineas
        sal.append("end")
        return "\n".join(sal) + "\n"


def main(args):
    salida = "--stdout" in args
    solo = "--check" in args
    rutas = [a for a in args if not a.startswith("--")]
    if not rutas:
        print(__doc__)
        return 2
    mal = 0
    for r in rutas:
        try:
            texto = Generador(r).generar()
        except ErrorEscena as e:
            print("escena: %s" % e, file=sys.stderr)
            mal += 1
            continue
        except (OSError, KeyError, ValueError, TypeError) as e:
            print("escena: %s: %s" % (r, e), file=sys.stderr)
            mal += 1
            continue
        if salida:
            sys.stdout.write(texto)
        elif not solo:
            open(os.path.splitext(r)[0] + ".dash", "w", encoding="utf-8").write(texto)
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
