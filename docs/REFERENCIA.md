# Referencia de Fragua

Sacada de `api/fragua.json` con `tools/gen_referencia.py`: no se edita a mano. El formato de las escenas está en `docs/ESCENAS.md`.

## Funciones

### El árbol

- `run(root: Node)`: El bucle del juego hasta quit(): física a paso fijo, process, señales, dibujo. Abre una pantalla de 320x256 y 5 planos si no hay ninguna.
  `run(scene_level1())`
- `quit()`: Acaba run() al final del fotograma.
- `change_scene(root: Node)`: Cambia el árbol entero al acabar el fotograma (el viejo se libera).
  `change_scene(scene_level2())`
- `get_tree_root() -> Node`: La raíz del árbol.
- `get_nodes_in_group(g: String) -> [Node]`: Los nodos de un grupo.
  `for e in get_nodes_in_group("enemies")`
- `node_by_id(id: Int) -> Node`: El nodo de ese id (el data de las señales de choque), o nil.
- `id_in_group(id: Int, g: String) -> Bool`: El nodo de ese id está en el grupo.
- `set_paused(p: Bool)`: Pausa: nada se mueve; se sigue dibujando.
- `set_frame_rate(rate: Int)`: 25 fotogramas por segundo en vez de 50, con la física a 50.
- `set_active_margin(margin: Int)`: Con cámara, los nodos más lejos que esto de la vista se quedan quietos (-1: nunca).

### Métodos de Node

- `n.add_child(c: Node)`: Añade un hijo (si el padre está en el árbol, entra y recibe ready).
- `n.remove_child(c: Node)`: Lo saca del árbol sin liberarlo.
- `n.queue_free()`: Fuera del árbol y liberado al acabar el fotograma.
- `n.get_node(path: String) -> Node`: Un nodo por su ruta: "Jugador/Arma", "..", "/Nivel/Jugador".
  `arma = jugador.get_node("Arma")`
- `n.find(name: String) -> Node`: El primero con ese nombre debajo, a cualquier profundidad.
- `n.global_x() -> Int, n.global_y() -> Int`: Posición en el mundo.
- `n.set_pos(x, y), n.set_global_pos(x, y)`: Pone la posición (desde el padre, o en el mundo).
- `n.add_to_group(g), n.remove_from_group(g), n.is_in_group(g)`: Grupos de nodos.
- `n.emit(signal: String, data: Int)`: Emite una señal: la reciben su script, sus comportamientos y los nodos conectados, al acabar el fotograma.
  `n.emit("opened", 0)`
- `n.connect(signal: String, to: Node), n.disconnect(signal, to)`: Conecta una señal de n con otro nodo (su on_signal).
  `timer.connect("timeout", jefe)`
- `n.add_behavior(b: Script)`: Pone un comportamiento listo (Platformer(), Patrol()...).
  `jugador.add_behavior(Platformer())`
- `n.set_z_index(z: Int)`: Orden de dibujo.
- `n.play(anim: String), n.stop(), n.start()`: Animación, sonido, Timer o partículas, según el tipo.
- `n.set_text(t: String)`: Texto de un Label.
- `n.move_and_slide()`: Body2D: se mueve por su velocidad y se para en paredes, suelo y cuerpos sólidos.
- `n.hitbox() -> Rect, n.overlaps(o: Node) -> Bool, n.touches_tile(kind) -> Bool`: Choques a mano.

### Física

- `accelerate_x(n, target: Fixed, rate: Fixed), accelerate_y(...)`: Hacia una velocidad, tanto por paso: inercia, aceleración y frenada.
  `accelerate_x(n, Fixed(3) * dir, Fixed(0.2))`
- `friction_x(n, amount: Fixed)`: Rozamiento: la velocidad en x hacia 0.
- `apply_gravity(n, g: Fixed, max_fall: Fixed)`: Gravedad hasta una velocidad de caída.
- `tile_at(wx: Int, wy: Int) -> Int`: La casilla de choque en un punto del mundo (TILE_SOLID...).

### El mundo

- `new_tilemap(name, file) -> Node, new_tilemap_with(name, file, tileset)`: Un mapa .fmap del editor de Forja.
- `map_objects(map, kind) -> [Int], map_object_x(map, i), map_object_y(map, i), map_object_name(map, i)`: Los objetos del mapa ("enemy", "coin"...).
- `map_pixel_width(map), map_pixel_height(map)`: Tamaño del mapa en píxeles (para los límites de la cámara).
- `set_view(x, y, w, h)`: Dónde se ve el mundo en la pantalla (el resto, para el marcador).
- `set_background_color(pen), set_hud_color(pen)`: Colores del fondo y de fuera de la vista.
- `redraw_background()`: Pinta otra vez el fondo (mapas, ColorRect, Labels).
- `set_isometric(on: Bool), set_iso_origin(x0)`: Proyección isométrica: suelo en rombos, orden por profundidad.
- `image_cached(file) -> Image, sound_cached(file) -> Int`: Imágenes y sonidos cargados una vez.
- `spawn(n: Node, s: Node, dx, dy) -> Node`: Pone un árbol nuevo (una escena) junto a n, como hermano.
  `spawn(n, scene_bullet(), 8, 0)`

### Entrada

- `action_pressed(name), action_just_pressed(name), action_just_released(name)`: Acciones: left, right, up, down, jump, fire, pause, quit (teclas y joystick).
- `action_axis(neg, pos) -> Int`: -1, 0 o 1 de dos acciones.
  `dx = action_axis("left", "right")`
- `action_add(name, code)`: Otra tecla (o JOY_FIRE...) para una acción.
- `action_force(name, down)`: El programa mantiene una acción (demo, pruebas, jugador de la máquina).

### Variables del juego

- `game_get(name), game_set(name, v), game_add(name, v)`: Variables del juego (puntos, vidas, tiempo).
- `bind_label(n, prefix, var_name)`: Un Label que enseña una variable del juego.

### Sonido

- `play_sound(file), play_music(file), stop_music()`: Efectos 8SVX y música MOD.

### Efectos

- `tween(n, prop, to, frames), tween_ease(n, prop, to, frames, ease)`: Una propiedad (x, y, z_index, frame) hacia un valor; señal tween_finished.

### Para comportamientos

- `play_facing(n, anim, facing), move_node(n, dx, dy), send_signal(to, name, from, data)`: Ayudas que usan los comportamientos.

## Nodos

### Propiedades de todos los nodos

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `x` | Int | `0` | -32768 … 32767 | Posición x, desde el padre (píxeles) |
| `y` | Int | `0` | -32768 … 32767 | Posición y, desde el padre |
| `z_index` | Int | `0` | -100 … 100 | Orden de dibujo: más alto, delante |
| `visible` | Bool | true |  | Se ve (con sus hijos) |
| `ui` | Bool | false |  | En coordenadas de pantalla: la cámara no lo mueve (marcador, menús) |
| `paused` | Bool | false |  | Sin process, physics_process ni comportamientos |

### Node

Un nodo sin más: agrupa a otros (la raíz de un nivel).

Se crea con: `new_node(name)`

### Node2D

Un nodo con posición: sus hijos se mueven con él.

Se crea con: `new_node2d(name, x, y)`

### Sprite2D

Una imagen (un BOB) con el color 0 transparente; su esquina de arriba a la izquierda en el nodo.

Se crea con: `new_sprite2d(name, image, x, y)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `image` | Image | — |  | Fichero IFF del editor de sprites de Forja |
| `frame` | Int | `0` | 0 … 255 | Fotograma que enseña |
| `offset` | Point | `[0, 0]` |  | Desplazamiento de la imagen desde el nodo |

### AnimatedSprite2D

Una imagen con animaciones con nombre (fotogramas y velocidad). play("walk").

Se crea con: `new_animated_sprite2d(name, image, x, y)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `image` | Image | — |  | Fichero IFF con los fotogramas |
| `animations` | Animations | `{}` |  | Animaciones: nombre -> fotogramas, velocidad (fotogramas de vídeo por fotograma) y si se repite |
| `autoplay` | String | — |  | Animación que suena al empezar |
| `offset` | Point | `[0, 0]` |  | Desplazamiento de la imagen |

Señales: `animation_finished` (Acabó una animación que no se repite)

### HardwareSprite2D

Un sprite de hardware: no cuesta CPU; 16 píxeles de ancho, 3 colores, como mucho 7.

Se crea con: `new_hw_sprite2d(name, file, x, y)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `image` | Image | — |  | IFF con fotogramas de 16 de ancho |
| `frame` | Int | `0` | 0 … 255 | Fotograma |

### CollisionShape2D

La forma de choque de su padre (Body2D o Area2D): una caja o un círculo.

Se crea con: `new_shape_rect(name, x, y, w, h) / new_shape_circle(name, x, y, r)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `rect` | Rect | `[0, 0, 16, 16]` |  | Caja: x, y, ancho, alto |
| `circle` | Circle | — |  | Círculo: x, y del centro y radio |

### Body2D

Un cuerpo que se mueve con move_and_slide() y se para en las paredes del mapa y en los cuerpos sólidos.

Se crea con: `new_body2d(name, x, y)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `layer` | Int | `1` | 0 … 65535 | Capas en las que está (bits) |
| `mask` | Int | `1` | 0 … 65535 | Capas de los cuerpos sólidos con los que choca |
| `collide_map` | Bool | true |  | Choca con el mapa de tiles |
| `solid` | Bool | false |  | Los demás cuerpos se paran en él |
| `bounce` | Fixed | `0` | 0 … 1 | Rebote: 0 se para, 1 vuelve igual de rápido |

Señales: `landed` (Tocó el suelo (data: velocidad de caída en 1/16 de píxel)), `collided` (Se paró en un cuerpo sólido (data: su id))

### StaticBody2D

Un cuerpo que no se mueve solo y para a los demás (pared, caja, plataforma móvil).

Se crea con: `new_static_body2d(name, x, y)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `layer` | Int | `1` | 0 … 65535 | Capas en las que está (bits) |

### Area2D

Una zona que avisa de quién entra y sale; no empuja.

Se crea con: `new_area2d(name, x, y)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `layer` | Int | `1` | 0 … 65535 | Capas en las que está |
| `mask` | Int | `1` | 0 … 65535 | Capas de lo que ve |
| `monitoring` | Bool | true |  | Mira quién entra |

Señales: `body_entered` (Entró un cuerpo (data: su id)), `body_exited` (Salió un cuerpo), `area_entered` (Entró otra área), `area_exited` (Salió otra área)

### TileMap

Un mapa del editor de mapas de Forja (.fmap): sus capas se pintan en el fondo; la capa de choques para a los cuerpos.

Se crea con: `new_tilemap(name, file)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `file` | Map | — |  | Fichero .fmap |
| `tileset` | Image | — |  | Otro tileset (si no, el del mapa) |
| `iso` | Bool | false |  | Isométrico: tiles en rombo |
| `spawn` | Spawn | `{}` |  | Clase de objeto del mapa -> escena que se pone en su sitio |

### Camera2D

La cámara: sigue a un nodo, una pantalla cada vez, dentro de sus límites.

Se crea con: `new_camera2d(name)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `target` | NodePath | — |  | Ruta del nodo que sigue |
| `limits` | Limits | `"map"` |  | Tamaño del mundo, o "map": el del primer mapa |

### Label

Un texto. Con bg >= 0 se pinta en el fondo solo al cambiar (barato).

Se crea con: `new_label(name, x, y, text, pen, bg)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `text` | String | — |  | El texto |
| `pen` | Color | `1` | 0 … 255 | Color del texto |
| `bg` | Color | `0` | -1 … 255 | Color de la caja (-1: encima en cada fotograma) |
| `bind` | String | — |  | Variable del juego que enseña |
| `prefix` | String | — |  | Texto delante del valor |

### Timer

Avisa (timeout) al cabo de un tiempo, una vez o siempre.

Se crea con: `new_timer(name, wait, one_shot)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `wait` | Int | `50` | 1 … 100000 | Fotogramas de vídeo (50 son un segundo) |
| `one_shot` | Bool | false |  | Una vez |
| `autostart` | Bool | false |  | Empieza al entrar en el árbol |

Señales: `timeout` (Pasó el tiempo)

### AudioPlayer

Un efecto de sonido (8SVX): play() lo suena.

Se crea con: `new_audio(name, file, channel)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `file` | Sound | — |  | Fichero 8SVX |
| `channel` | Int | `-1` | -1 … 3 | Canal 0 a 3 (-1: el primero libre) |
| `volume` | Int | `64` | 0 … 64 | Volumen |

### Particles2D

Unos puntos que salen y caen (chispas, polvo): start() los suelta.

Se crea con: `new_particles2d(name, x, y, amount, pen)`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `amount` | Int | `8` | 1 … 64 | Cuántos |
| `pen` | Color | `1` | 0 … 255 | Color |
| `lifetime` | Int | `25` | 1 … 500 | Fotogramas que duran |
| `speed` | Int | `24` | 0 … 256 | Velocidad (1/16 de píxel) |
| `gravity` | Int | `2` | -32 … 32 | Gravedad (1/16 de píxel) |
| `size` | Int | `2` | 1 … 8 | Lado de cada punto |
| `one_shot` | Bool | true |  | Una vez por start() |

## Comportamientos listos

### Platformer

Corre y salta con gravedad (flechas o joystick, espacio o disparo). Pone las animaciones idle, walk y jump (y _left).

`n.add_behavior(Platformer())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `speed` | Fixed | `2` | 0 … 16 | Velocidad máxima |
| `accel` | Fixed | `0.25` | 0 … 4 | Aceleración por paso |
| `friction` | Fixed | `0.3` | 0 … 4 | Frenada sin mando |
| `gravity` | Fixed | `0.35` | 0 … 4 | Gravedad |
| `max_fall` | Fixed | `6` | 0 … 16 | Velocidad máxima de caída |
| `jump` | Fixed | `5.5` | 0 … 16 | Fuerza del salto |
| `jumps` | Int | `1` | 0 … 5 | Saltos seguidos (2: doble salto) |
| `player` | Bool | true |  | Lo mueve el jugador (si no, dir y want_jump) |

Señales: `jumped` (Saltó)

### EightWay

Se mueve en ocho direcciones (vista cenital).

`n.add_behavior(EightWay())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `speed` | Fixed | `2` | 0 … 16 | Velocidad |
| `accel` | Fixed | `0.5` | 0 … 16 | Aceleración |
| `player` | Bool | true |  | Lo mueve el jugador |

### Bullet

Va en línea recta; con cuerpo, se quita al dar en una pared.

`n.add_behavior(Bullet())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `vx` | Fixed | `4` | -16 … 16 | Velocidad x |
| `vy` | Fixed | `0` | -16 … 16 | Velocidad y |
| `destroy_on_wall` | Bool | true |  | Se quita al chocar |

### Follow

Va hacia otro nodo (por ruta o "group:nombre").

`n.add_behavior(Follow())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `target` | NodePath | `"/Player"` |  | Ruta o grupo del que sigue |
| `speed` | Fixed | `1` | 0 … 16 | Velocidad |
| `distance` | Int | `0` | 0 … 320 | Se para a esta distancia |
| `only_x` | Bool | false |  | Solo en x (un rival en una carrera) |

### Patrol

Anda en una dirección y se da la vuelta en paredes y bordes.

`n.add_behavior(Patrol())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `speed` | Fixed | `0.75` | 0 … 8 | Velocidad |
| `dir` | Int | `-1` | -1 … 1 | Dirección al empezar |
| `gravity` | Fixed | `0.35` | 0 … 4 | Gravedad (0: vuela) |
| `turn_at_edges` | Bool | true |  | Se vuelve en los bordes del suelo |

### BounceEdges

Rebota en los bordes del mundo (la pelota del Pong).

`n.add_behavior(BounceEdges())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `vx` | Fixed | `2` | -16 … 16 | Velocidad x |
| `vy` | Fixed | `2` | -16 … 16 | Velocidad y |
| `left` | Bool | true |  | Rebota a la izquierda |
| `right` | Bool | true |  | Rebota a la derecha |
| `top` | Bool | true |  | Rebota arriba |
| `bottom` | Bool | true |  | Rebota abajo |

Señales: `bounced` (Rebotó (data: 0 en x, 1 en y))

### Wrap

Sale por un lado del mundo y entra por el otro.

`n.add_behavior(Wrap())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `margin` | Int | `0` | 0 … 320 | Margen |

### DestroyOffscreen

Se quita al salir del mundo.

`n.add_behavior(DestroyOffscreen())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `margin` | Int | `32` | 0 … 320 | Margen |

Señales: `left_world` (Salió del mundo)

### Health

Vida: oye "damage" y "heal"; parpadea tras un golpe.

`n.add_behavior(Health())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `hp` | Int | `3` | 1 … 1000 | Vida |
| `max_hp` | Int | `3` | 1 … 1000 | Vida máxima |
| `invulnerable` | Int | `50` | 0 … 500 | Fotogramas sin daño tras un golpe |
| `destroy` | Bool | true |  | Se quita al morir |
| `var_name` | String | — |  | Variable del juego con la vida |

Señales: `hurt` (Recibió daño (data: vida que le queda)), `died` (Se quedó sin vida)

### Damage

Daña a los del grupo que toca.

`n.add_behavior(Damage())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `group` | String | `"player"` |  | Grupo al que daña |
| `amount` | Int | `1` | 1 … 1000 | Daño |
| `destroy_self` | Bool | false |  | Se quita al dañar (una bala) |

### Pickup

Se recoge: suma a una variable, suena y se quita.

`n.add_behavior(Pickup())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `group` | String | `"player"` |  | Grupo que lo recoge |
| `var_name` | String | `"score"` |  | Variable del juego |
| `amount` | Int | `1` | -1000 … 1000 | Cuánto suma |
| `sound` | Sound | — |  | Sonido al recogerlo |

Señales: `picked` (Lo recogieron (data: id de quién))

### Draggable

El ratón lo arrastra.

`n.add_behavior(Draggable())`

Señales: `drag_started` (Empezó a arrastrarse), `dropped` (Se soltó)

### Blink

Parpadea un rato o siempre.

`n.add_behavior(Blink())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `period` | Int | `8` | 1 … 100 | Fotogramas encendido y apagado |
| `duration` | Int | `0` | 0 … 10000 | Cuánto dura (0: siempre) |

Señales: `blink_finished` (Acabó de parpadear)

### Vehicle

Coche o moto de lado: acelera, frena, inercia, marchas, salta; avisa si aterriza demasiado rápido.

`n.add_behavior(Vehicle())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `accel` | Fixed | `0.08` | 0 … 2 | Aceleración por paso |
| `brake` | Fixed | `0.2` | 0 … 2 | Frenada |
| `drag` | Fixed | `0.02` | 0 … 2 | Rozamiento sin mando |
| `gears` | Int | `3` | 1 … 6 | Marchas |
| `gear_speed` | Fixed | `1.5` | 0 … 8 | Velocidad máxima por marcha |
| `gravity` | Fixed | `0.3` | 0 … 4 | Gravedad |
| `jump` | Fixed | `5` | 0 … 16 | Fuerza del salto |
| `crash_speed` | Int | `96` | 0 … 512 | Velocidad de caída que estrella (1/16 de píxel) |
| `player` | Bool | true |  | Lo lleva el jugador |

Señales: `gear` (Cambió de marcha (data: la marcha)), `jumped` (Saltó), `crashed` (Aterrizó demasiado rápido (data: velocidad))

### Sine

Sube y baja (o va y viene) alrededor de donde empezó.

`n.add_behavior(Sine())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `amplitude` | Int | `8` | 0 … 320 | Cuánto se aparta (píxeles) |
| `period` | Int | `100` | 2 … 10000 | Fotogramas por vuelta |
| `horizontal` | Bool | false |  | Va y viene en x |

### Shooter

Emite "shoot" cada cierto tiempo o al pulsar una acción; un evento crea la bala (acción spawn).

`n.add_behavior(Shooter())`

| Propiedad | Tipo | Por defecto | Rango | Qué es |
|---|---|---|---|---|
| `every` | Int | `25` | 1 … 1000 | Fotogramas entre disparos |
| `action` | String | — |  | Acción que dispara (vacío: solo) |

Señales: `shoot` (Toca disparar)

## Acciones de los eventos

| `do` | Qué es | Código |
|---|---|---|
| `add` | Suma a una variable del juego | `game_add(VAR, VALUE)` |
| `set` | Pone una variable del juego | `game_set(VAR, VALUE)` |
| `sound` | Suena un efecto | `play_sound(FILE)` |
| `music` | Empieza una música MOD | `play_music(FILE)` |
| `destroy` | Quita este nodo (o el otro) | `n.queue_free()` |
| `emit` | Emite una señal | `n.emit(SIGNAL, DATA)` |
| `damage` | Daña al otro | `send_signal(other, "damage", n, VALUE)` |
| `spawn` | Pone una copia de otra escena junto a este nodo | `spawn(n, scene_X(), X, Y)` |
| `play` | Pone una animación | `n.get_node(TARGET).play(ANIM)` |
| `start` | Arranca un Timer o unas partículas | `n.get_node(TARGET).start()` |
| `show` | Lo enseña | `n.visible = true` |
| `hide` | Lo esconde | `n.visible = false` |
| `change_scene` | Cambia de escena | `change_scene(scene_X())` |
| `quit` | Acaba el juego | `quit()` |
| `code` | Dash escrito a mano | `DASH` |
