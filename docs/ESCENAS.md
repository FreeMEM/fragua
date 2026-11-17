# Escenas de Fragua: el formato `.escena`

Una escena es un árbol de nodos guardado en un fichero, como en Godot. El editor de escenas de Forja la escribe, y
`tools/escena.py` (o Forja, al guardar) la convierte en un `.dash` normal (forma B del diseño): una función que
monta el árbol. El juego importa ese `.dash` y llama a la función cada vez que quiere una copia.

```
python3 tools/escena.py enemigo.escena          # escribe enemigo.dash al lado
```

```
import "fragua/fragua.dash"
import "enemigo.dash"

    e = scene_enemigo()          # un árbol nuevo cada vez: diez enemigos, diez llamadas
    nivel.add_child(e)
```

El `.dash` generado se lee bien a propósito: quien quiera pasar a programar ve ahí lo que hace la escena, con las
mismas funciones que escribiría a mano. No se edita: se edita la escena y se genera otra vez.

## El fichero

JSON en UTF-8. Ejemplo (`examples/plataformas/enemy.escena`):

```json
{
  "fragua": 1,
  "name": "Enemy",
  "root": {
    "type": "Body2D",
    "name": "Enemy",
    "props": {"layer": 2},
    "groups": ["enemies"],
    "script": "Enemy",
    "behaviors": [{"type": "Patrol", "props": {"speed": 0.75}}],
    "children": [
      {"type": "AnimatedSprite2D", "name": "Sprite",
       "props": {"image": "enemy.iff",
                 "animations": {"walk": {"frames": [0, 1], "speed": 8, "loop": true}},
                 "autoplay": "walk"}},
      {"type": "CollisionShape2D", "name": "Shape", "props": {"rect": [1, 4, 14, 12]}}
    ]
  }
}
```

- `fragua`: la versión del formato (1).
- `name`: el nombre de la escena. La función generada es `scene_` más el nombre en minúsculas, con `_` en vez de
  lo que no sea letra o cifra: `scene_enemy()`.
- `projection` (opcional): `"flat"` (la de siempre) o `"iso"` (isométrica: la función generada llama a
  `set_isometric(true)`). Es de la escena, no de cada nodo.
- `root`: el nodo raíz. Cada nodo tiene:
  - `type`: uno de los tipos de la tabla de abajo, o `"Instance"` (otra escena, ver abajo).
  - `name`: su nombre (para `get_node`). Único entre sus hermanos.
  - `props`: sus propiedades; las que falten toman el valor por defecto. Las de cada tipo, con su tipo, valor por
    defecto y rango, están en `api/fragua.json` (lo que enseña el inspector de Forja).
  - `groups`: los grupos en los que entra.
  - `script`: el nombre de un struct del juego que cumple `Script`. Se crea con `Nombre()`: sus campos necesitan
    valor por defecto.
  - `behaviors`: comportamientos listos (`Platformer`, `Patrol`, `Pickup`...) con sus propiedades.
  - `events`: eventos con acciones, sin código (abajo).
  - `children`: sus hijos, en orden de dibujo dentro del mismo `z_index`.
- `connections` (opcional, en la escena): `[{"from": "Timer", "signal": "timeout", "to": "."}]`. Rutas desde la raíz
  de la escena (`"."` es la raíz). La señal llega al `on_signal` del script y los comportamientos de `to`.

### Tipos de nodo

| `type` | Se crea con | Propiedades propias |
|---|---|---|
| `Node` | `new_node` | — |
| `Node2D` | `new_node2d` | — |
| `Sprite2D` | `new_sprite2d` | `image`, `frame`, `offset` |
| `AnimatedSprite2D` | `new_animated_sprite2d` | `image`, `animations`, `autoplay`, `offset` |
| `HardwareSprite2D` | `new_hw_sprite2d` | `image` (frames de 16 de ancho, 3 colores) |
| `CollisionShape2D` | `new_shape_rect` o `new_shape_circle` | `rect: [x, y, w, h]` o `circle: [x, y, r]` |
| `Body2D` | `new_body2d` | `layer`, `mask`, `collide_map`, `solid`, `bounce` |
| `StaticBody2D` | `new_static_body2d` | `layer`, `mask` |
| `Area2D` | `new_area2d` | `layer`, `mask`, `monitoring` |
| `TileMap` | `new_tilemap` | `file` (un `.fmap`), `tileset`, `iso`, `spawn` |
| `Camera2D` | `new_camera2d` | `target` (ruta), `limits: [w, h]` o `"map"` |
| `Label` | `new_label` | `text`, `pen`, `bg`, `bind`, `prefix` |
| `Timer` | `new_timer` | `wait`, `one_shot`, `autostart` |
| `AudioPlayer` | `new_audio` | `file`, `channel`, `volume` |
| `Particles2D` | `new_particles2d` | `amount`, `pen`, `lifetime`, `speed`, `gravity`, `size`, `one_shot` |

Todos tienen además `x`, `y`, `z_index`, `visible`, `ui` y `paused`.

`TileMap` con `spawn`: `{"enemy": "enemy.escena", "coin": "coin.escena"}` crea, por cada objeto del mapa de esa
clase, una copia de la escena en su sitio, como hermana del mapa.

### Escenas dentro de escenas

```json
{"type": "Instance", "name": "Enemy1", "scene": "enemy.escena", "props": {"x": 120, "y": 64}}
```

Llama a la función de la otra escena y le pone las propiedades de nodo (`x`, `y`, `z_index`, `visible`...). El
`.dash` generado importa el de la otra escena.

### Eventos y acciones (sin código)

Un evento es "cuando llegue esta señal a este nodo (y se cumpla esto), haz esto otro". Se guardan en el nodo:

```json
"events": [
  {"signal": "body_entered", "if_group": "player",
   "actions": [{"do": "add", "var": "score", "value": 10},
               {"do": "sound", "file": "coin.8svx"},
               {"do": "destroy"}]}
]
```

- `signal`: la señal (las de cada tipo y comportamiento, en `api/fragua.json`).
- `if_group` (opcional): el otro nodo de la señal (el de `data`, en las de choque) está en ese grupo.
- `if` (opcional): una condición escrita en Dash (`game_get("score") >= 100`).
- `actions`, en orden:

| `do` | Qué hace | Código que genera |
|---|---|---|
| `add` | suma a una variable del juego | `game_add("score", 10)` |
| `set` | pone una variable del juego | `game_set("level", 2)` |
| `sound` | suena un efecto | `play_sound("coin.8svx")` |
| `music` | empieza una música MOD | `play_music("song.mod")` |
| `destroy` | quita este nodo (`"target": "other"`: el otro) | `n.queue_free()` |
| `emit` | emite una señal de este nodo | `n.emit("opened", 0)` |
| `damage` | daña al otro (`value`) | `send_signal(other, "damage", n, 1)` |
| `spawn` | una copia de otra escena junto a este nodo (`x`, `y`) | `spawn(n, scene_bullet(), 8, 0)` |
| `play` | una animación (`target`: ruta del sprite) | `n.get_node("Sprite").play("die")` |
| `start` | arranca un Timer o unas partículas (`target`) | `n.get_node("Timer").start()` |
| `show`, `hide` | enseña o esconde (`target` opcional) | `n.visible = true` |
| `change_scene` | cambia de escena | `change_scene(scene_level2())` |
| `quit` | acaba el juego | `quit()` |
| `code` | Dash escrito a mano (`dash`) | lo que diga |

Los eventos de un nodo se generan como un struct `<Escena><Nodo>Events` con `Script`, puesto en el nodo como un
comportamiento más. En su `on_signal`, `n` es el nodo y `other` el de `data` (`node_by_id(data)`).

## Lo que genera

Para el enemigo de arriba:

```
# Generated by Fragua (tools/escena.py) from enemy.escena: edit the scene, not this file.

func scene_enemy() -> Node
    n1 = new_body2d("Enemy", 0, 0)
    n1.body.layer = 2
    n1.add_to_group("enemies")
    n1.script = Enemy()
    b1 = Patrol()
    b1.speed = Fixed(0.75)
    n1.add_behavior(b1)
    n2 = new_animated_sprite2d("Sprite", image_cached("enemy.iff"), 0, 0)
    add_animation(n2, "walk", [0, 1], 8, true)
    n2.play("walk")
    n1.add_child(n2)
    n3 = new_shape_rect("Shape", 1, 4, 14, 12)
    n1.add_child(n3)
    return n1
end
```

Las imágenes y los sonidos se cargan una vez (`image_cached`, `sound_cached`): diez enemigos comparten la imagen.
