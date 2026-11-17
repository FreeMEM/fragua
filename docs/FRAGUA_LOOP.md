# Fragua, capa 2: plan y bitácora

Rama `nodos` (worktree `.worktrees/nodos`). Diseño de partida: `docs/JUEGOS_DISENO.md` de Forja (secciones 1b y 7).
Fragua es el producto estrella junto a Forja (usuario, 2026-11-17): API cuidada y documentada en castellano e
inglés, ejemplos que luzcan, medidas en las máquinas de verdad y todo lo que el editor de escenas de Forja va a
necesitar (formato de escena, propiedades exportadas, plantilla de juego, ayuda y autocompletado).

## Decisiones de esta capa

1. **Un solo struct `Node` para todos los tipos.** Dash no deja bajar de una interfaz a su struct, así que si cada
   tipo fuera un struct distinto, `get_node("Jugador/Arma")` no daría acceso a sus campos. `Node` lleva lo común
   (nombre, hijos, padre `weak`, posición, grupos, señales) y un campo por tipo que solo se rellena en los nodos de
   ese tipo: `n.body`, `n.sprite`, `n.shape`, `n.area`, `n.map`, `n.camera`, `n.label`, `n.timer`, `n.audio`,
   `n.particles`. `get_node` devuelve un `Node` con todo a mano.
2. **Interfaces para el comportamiento:** `Script` (`_ready`, `_process`, `_physics_process`, `_signal`) es lo que
   cumple el código del usuario y también cada comportamiento listo. Un nodo tiene un script (`n.script`) y una
   lista de comportamientos (`n.behaviors`), como GameMaker y Construct.
3. **Señales sin funciones:** las lambdas de Dash no ven variables locales, así que `n.emit("hit", dato)` pone la
   señal en una cola y, una vez por fotograma, cada nodo conectado (`a.connect("hit", b)`) la recibe en
   `_signal(b, "hit", a, dato)`, en su script y en sus comportamientos.
4. **Paso fijo de 50 Hz** (60 en NTSC): `_physics_process` una vez por fotograma de vídeo; si el juego se retrasa,
   dos o tres veces antes de pintar.
5. **Coordenadas enteras en píxeles** para la posición; velocidades y restos en `Fixed` (16.16), en el cuerpo.
6. **Dibujo con rectángulos sucios:** la pantalla guarda un fondo (el mapa de tiles y el marcador). Cada cosa
   pintada apunta su rectángulo en el búfer donde se pintó, y al volver a ese búfer se repone el fondo solo ahí.
7. **Cámara por pantallazos.** Dash no tiene scroll de hardware, y repintar el mapa entero cuesta más de un
   fotograma. La cámara salta de pantalla en pantalla (como Rick Dangerous o Prince of Persia).
8. **Escenas, forma B:** un `.escena` (JSON) que Forja convierte en un `.dash` normal. Fragua define el formato y
   trae el conversor de referencia (`tools/escena.py`), que usan las pruebas y los ejemplos.
9. **Programar sin programar:** comportamientos listos con propiedades, propiedades exportadas descritas en
   `api/fragua.json` (tipo, valor por defecto, rango, ayuda en los dos idiomas) y eventos con acciones guardados en
   la escena, que el conversor pasa a código Dash legible.

## Fases y pasos (cada paso se comprueba)

### A. Árbol de nodos (hecho si pasa `tests/nodos.dash`)
- A1. `Node`: `add_child`, `remove_child`, `queue_free`, `get_node("a/b")`, `..`, `find`, grupos, ids.
- A2. El árbol (`tree`): `run(raiz)`, `_ready` de hijos antes que del padre, `_process(delta)`,
  `_physics_process` a paso fijo, `quit()`, `change_scene(raiz)` al acabar el fotograma.
- A3. Señales: `emit`, `connect`, `disconnect`, cola repartida una vez por fotograma.

### B. Dibujo
- B1. Sprite (BOB, imagen de Forja) y sprite de hardware (`hardware`), con rectángulos sucios por búfer.
- B2. AnimatedSprite: animaciones con nombre, fotogramas y velocidad; señal `animation_finished`.
- B3. TileMap: un `.fmap` del editor de mapas de Forja pintado en el fondo; capa de choques.
- B4. Camera: sigue a un nodo por pantallazos, con límites; los nodos `ui` no se mueven con ella.
- B5. Label: texto en el fondo (barato) o encima en cada fotograma; enlazado a una variable del juego.
- B6. Recorte: nada se pinta fuera de la pantalla (`bob_paste` no recorta).

### C. Física y choques
- C1. Shape: caja o círculo, hija de un Body o un Area.
- C2. Body cinemático: `move_and_slide()` con el mapa (sólido, plataforma de un sentido, escalera, daño y
  pendientes) y con otros cuerpos sólidos; `on_floor`, `on_wall`, `on_ceiling`; rebote.
- C3. Ayudas de movimiento: gravedad, aceleración hacia una velocidad, rozamiento, salto.
- C4. Area: `body_entered`, `body_exited`, `area_entered`; capas y máscaras de bits, como Godot.

### D. Tiempo, sonido y efectos
- D1. Timer (`timeout`), AudioPlayer (efecto en un canal; música MOD), partículas sencillas, tweens.

### E. Comportamientos listos (structs que cumplen `Script`)
Platformer, EightWay, Bullet, Follow, Patrol, BounceEdges, Wrap, DestroyOffscreen, Health, Pickup, Draggable,
Blink. Cada uno con sus propiedades exportadas en `api/fragua.json`.

### F. Escenas y eventos sin código
- F1. Formato `.escena` (JSON), con nodos, propiedades, scripts, comportamientos, escenas dentro de escenas y
  eventos con acciones. Documento: `docs/ESCENAS.md`.
- F2. `tools/escena.py`: `.escena` → `.dash` legible (lo que hará Forja). Instanciar varias veces.
- F3. Variables del juego (`game_add("score", 10)`) y acciones (`sumar`, `sonar`, `destruir`, `cambiar escena`...).

### G. Ejemplos, pruebas y medidas
- G1. Plataformas con `.fmap`, jugador, enemigos de una escena, monedas con señales, cámara y marcador.
- G2. Pong con nodos.
- G3. Pruebas en FS-UAE, A1200 y A500, con `./dash` y con `./dash --gcc`.
- G4. Medidas a velocidad real: nodos y sprites que caben a 50 Hz.

### H. Para Forja
- H1. `api/fragua.json`: funciones, nodos, propiedades exportadas, señales y comportamientos, con ayuda en
  castellano e inglés. `tools/gen_referencia.py` saca de ahí `docs/REFERENCIA.md` y `docs/REFERENCE.en.md`; de ahí
  también saldrán la ayuda y el autocompletado de Forja.
- H2. Plantilla de juego (`plantilla/`): escena principal, jugador y un nivel.
- H3. README en los dos idiomas.

### I. Tutorial y curso: un juego de motos de lado (lo hará otra tarea, sobre esta base)
Un juego original (nombre, gráficos, sonidos y niveles propios) de una moto que corre de lado y salta coches y
autobuses, como los de 8 bits de los 80. Todo el código y las imágenes. Sitio: `docs/tutorial/` (`moto.md` y
`moto.en.md`, un capítulo por paso) y `examples/moto/`. Lo que pide a Fragua, y dónde está:
- scroll horizontal largo y suave: `Camera` en modo `CAMERA_SCROLL` (necesita el scroll de hardware de Dash, ver
  abajo); mientras no lo haya, por pantallazos o con una franja que se desplaza;
- cuerpo con inercia, aceleración y frenada: `BodyData` con `accelerate_x`, `friction_x` y velocidad máxima
  (marchas = velocidades máximas distintas);
- saltos con gravedad, rampas (tiles en pendiente) y choques con obstáculos: aterrizar bien o estrellarse según la
  velocidad vertical y el ángulo al tocar suelo (`landed` con `data` = velocidad de caída);
- un rival que corre a la vez: otro `Body` con el comportamiento `Follow` o un script;
- marcador, tiempo y sonido de motor: `Label` enlazado a variables del juego, `Timer` y `AudioPlayer` en bucle con
  el tono (`sound_period`) según la velocidad.

## Lo que le falta a Dash (se apunta aquí con precisión)

Ver la sección del mismo nombre al final de la bitácora.

## Bitácora

### 2026-11-17
- Base escrita: `src/node.dash` (Node y sus datos por tipo, interfaz Script), `src/tree.dash` (árbol, grupos,
  señales, bucle), `src/world.dash` (mapas, cámara, etiquetas, dibujo), `src/physics.dash` (cajas, círculos,
  move_and_slide con mapa, plataformas, pendientes y cuerpos sólidos; áreas), `src/extras.dash` (acciones,
  variables del juego, sonido, partículas, tweens).
- Lo de Dash que salió:
  - `./dash --gcc`: `x.close()` dentro de un `if` o de una función da error de sintaxis (lo lee como el `Ventana.close` de las
    ventanas; `compiler/grammar.py`, regla `window_close: ID ".close"`). `./dash` lo compila bien.
  - `./dash`: un error de un struct que no cumple su interfaz sale con la línea de otro fichero (el último
    importado) en vez de la del struct.
  - `./dash --gcc`: un campo que empieza por "open" (`t.opened = true`) da "t is not a Window".
  - **Grave, los dos caminos:** liberar un objeto de un struct sin campos (`struct Oye: Script` con solo
    métodos) cuelga el Amiga. `struct _Dash_Oye {}` mide 0 y `_dash_obj_free` toma `t->size == 0` por un objeto
    de `_dash_rc_alloc` (el de tamaño guardado en un LONG delante de la cabecera): lee `h[-1]` y devuelve a la
    caché un bloque falso. Arreglo: dar tamaño 1 a los structs vacíos o marcar `_dash_any_type` de otra forma.
    Mientras, los scripts de Fragua necesitan al menos un campo. Caso mínimo: un struct vacío con interfaz,
    `a.script = Oye()` y `a.script = nil`.
  - `./dash`: los métodos de interfaz que empiezan por `_` (`_ready`) son privados del módulo: un struct de otro
    fichero no puede cumplir la interfaz ni llamarlos (`Scr no tiene el método _ready`). `--gcc` sí deja. Por eso
    los métodos de `Script` son `ready`, `process`, `physics_process` y `on_signal`, sin guion bajo.
  - `./dash`: `step` no vale como nombre de parámetro (lo toma por el `step` de `for`); `--gcc` sí lo deja.
  - Los builtins nuevos `image_load` y `screen_open` chocaban con la fase 1 de Fragua: ahora son `load_image` y
    `open_screen` (y, por coherencia, `new_image`, `new_clock`, `new_sprite`, `new_group`).
  - `./dash --gcc`: una `const` del programa llamada como una variable del runtime C (`const W = 320`, `const H`)
    sale como `#define W 320` y rompe el C del runtime (`_dash_tilemap_draw` usa `W` y `H`). El Pong con nodos
    usa `WORLD_W` y `WORLD_H`.
  - No se puede indexar lo que devuelve una llamada: `f()[0]` es error de sintaxis en los dos caminos.
