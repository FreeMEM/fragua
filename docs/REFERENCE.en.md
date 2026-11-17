# Fragua reference

Made from `api/fragua.json` by `tools/gen_referencia.py`: do not edit by hand. The scene format is in `docs/ESCENAS.md` (Spanish).

## Functions

### The tree

- `run(root: Node)`: The game loop until quit(): fixed-step physics, process, signals, drawing. Opens a 320x256 screen of 5 planes if none is open.
  `run(scene_level1())`
- `quit()`: Ends run() at the end of the frame.
- `change_scene(root: Node)`: Swaps the whole tree at the end of the frame (the old one is freed).
  `change_scene(scene_level2())`
- `get_tree_root() -> Node`: The root of the tree.
- `get_nodes_in_group(g: String) -> [Node]`: The nodes of a group.
  `for e in get_nodes_in_group("enemies")`
- `node_by_id(id: Int) -> Node`: The node of that id (the data of collision signals), or nil.
- `id_in_group(id: Int, g: String) -> Bool`: The node of that id is in the group.
- `set_paused(p: Bool)`: Pause: nothing moves; drawing goes on.
- `set_frame_rate(rate: Int)`: 25 frames a second instead of 50, with the physics at 50.
- `set_active_margin(margin: Int)`: With a camera, nodes further than this from the view stand still (-1: never).

### Node methods

- `n.add_child(c: Node)`: Adds a child (if the parent is in the tree, it enters and gets ready).
- `n.remove_child(c: Node)`: Takes it out of the tree without freeing it.
- `n.queue_free()`: Out of the tree and freed at the end of the frame.
- `n.get_node(path: String) -> Node`: A node by its path: "Player/Gun", "..", "/Level/Player".
  `arma = jugador.get_node("Arma")`
- `n.find(name: String) -> Node`: The first one with that name below, at any depth.
- `n.global_x() -> Int, n.global_y() -> Int`: Position in the world.
- `n.set_pos(x, y), n.set_global_pos(x, y)`: Sets the position (from the parent, or in the world).
- `n.add_to_group(g), n.remove_from_group(g), n.is_in_group(g)`: Groups of nodes.
- `n.emit(signal: String, data: Int)`: Emits a signal: its script, its behaviours and the connected nodes get it at the end of the frame.
  `n.emit("opened", 0)`
- `n.connect(signal: String, to: Node), n.disconnect(signal, to)`: Connects a signal of n to another node (its on_signal).
  `timer.connect("timeout", jefe)`
- `n.add_behavior(b: Script)`: Puts a ready-made behaviour (Platformer(), Patrol()...).
  `jugador.add_behavior(Platformer())`
- `n.set_z_index(z: Int)`: Drawing order.
- `n.play(anim: String), n.stop(), n.start()`: Animation, sound, Timer or particles, by kind.
- `n.set_text(t: String)`: Text of a Label.
- `n.move_and_slide()`: Body2D: moves by its speed and stops at walls, floor and solid bodies.
- `n.hitbox() -> Rect, n.overlaps(o: Node) -> Bool, n.touches_tile(kind) -> Bool`: Collisions by hand.

### Physics

- `accelerate_x(n, target: Fixed, rate: Fixed), accelerate_y(...)`: Towards a speed, so much a step: inertia, acceleration and braking.
  `accelerate_x(n, Fixed(3) * dir, Fixed(0.2))`
- `friction_x(n, amount: Fixed)`: Friction: the speed in x towards 0.
- `apply_gravity(n, g: Fixed, max_fall: Fixed)`: Gravity up to a falling speed.
- `tile_at(wx: Int, wy: Int) -> Int`: The collision tile at a world point (TILE_SOLID...).

### The world

- `new_tilemap(name, file) -> Node, new_tilemap_with(name, file, tileset)`: A .fmap map of Forja's editor.
- `map_objects(map, kind) -> [Int], map_object_x(map, i), map_object_y(map, i), map_object_name(map, i)`: The map's objects ("enemy", "coin"...).
- `map_pixel_width(map), map_pixel_height(map)`: Size of the map in pixels (for the camera's limits).
- `set_view(x, y, w, h)`: Where the world shows on the screen (the rest, for the score).
- `set_background_color(pen), set_hud_color(pen)`: Colours of the background and out of the view.
- `redraw_background()`: Paints the background again (maps, ColorRects, Labels).
- `set_isometric(on: Bool), set_iso_origin(x0)`: Isometric projection: diamond ground, drawn by depth.
- `image_cached(file) -> Image, sound_cached(file) -> Int`: Pictures and sounds loaded once.
- `spawn(n: Node, s: Node, dx, dy) -> Node`: Puts a new tree (a scene) next to n, as a brother.
  `spawn(n, scene_bullet(), 8, 0)`

### Input

- `action_pressed(name), action_just_pressed(name), action_just_released(name)`: Actions: left, right, up, down, jump, fire, pause, quit (keys and joystick).
- `action_axis(neg, pos) -> Int`: -1, 0 or 1 from two actions.
  `dx = action_axis("left", "right")`
- `action_add(name, code)`: Another key (or JOY_FIRE...) for an action.
- `action_force(name, down)`: The program holds an action (demo, tests, computer player).

### Game variables

- `game_get(name), game_set(name, v), game_add(name, v)`: Game variables (score, lives, time).
- `bind_label(n, prefix, var_name)`: A Label that shows a game variable.

### Sound

- `play_sound(file), play_music(file), stop_music()`: 8SVX effects and MOD music.

### Effects

- `tween(n, prop, to, frames), tween_ease(n, prop, to, frames, ease)`: A property (x, y, z_index, frame) towards a value; signal tween_finished.

### For behaviours

- `play_facing(n, anim, facing), move_node(n, dx, dy), send_signal(to, name, from, data)`: Helpers the behaviours use.

## Nodes

### Properties of every node

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `x` | Int | `0` | -32768 … 32767 | x position, from the parent (pixels) |
| `y` | Int | `0` | -32768 … 32767 | y position, from the parent |
| `z_index` | Int | `0` | -100 … 100 | Drawing order: higher, in front |
| `visible` | Bool | true |  | Shown (with its children) |
| `ui` | Bool | false |  | In screen coordinates: the camera does not move it (score, menus) |
| `paused` | Bool | false |  | No process, physics_process or behaviours |

### Node

A plain node: groups others (the root of a level).

Made with: `new_node(name)`

### Node2D

A node with a position: its children move with it.

Made with: `new_node2d(name, x, y)`

### Sprite2D

A picture (a BOB) with colour 0 transparent; its top left corner at the node.

Made with: `new_sprite2d(name, image, x, y)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `image` | Image | — |  | IFF file of Forja's sprite editor |
| `frame` | Int | `0` | 0 … 255 | Frame shown |
| `offset` | Point | `[0, 0]` |  | Offset of the picture from the node |

### AnimatedSprite2D

A picture with named animations (frames and speed). play("walk").

Made with: `new_animated_sprite2d(name, image, x, y)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `image` | Image | — |  | IFF file with the frames |
| `animations` | Animations | `{}` |  | Animations: name -> frames, speed (video frames a frame) and looping |
| `autoplay` | String | — |  | Animation playing at the start |
| `offset` | Point | `[0, 0]` |  | Offset of the picture |

Signals: `animation_finished` (An animation that does not loop finished)

### HardwareSprite2D

A hardware sprite: costs no CPU; 16 pixels wide, 3 colours, at most 7.

Made with: `new_hw_sprite2d(name, file, x, y)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `image` | Image | — |  | IFF with frames 16 wide |
| `frame` | Int | `0` | 0 … 255 | Frame |

### CollisionShape2D

The collision shape of its parent (Body2D or Area2D): a box or a circle.

Made with: `new_shape_rect(name, x, y, w, h) / new_shape_circle(name, x, y, r)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `rect` | Rect | `[0, 0, 16, 16]` |  | Box: x, y, width, height |
| `circle` | Circle | — |  | Circle: centre x, y and radius |

### Body2D

A body that moves with move_and_slide() and stops at the map's walls and at solid bodies.

Made with: `new_body2d(name, x, y)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `layer` | Int | `1` | 0 … 65535 | Layers it is in (bits) |
| `mask` | Int | `1` | 0 … 65535 | Layers of the solid bodies it stops at |
| `collide_map` | Bool | true |  | Collides with the tile map |
| `solid` | Bool | false |  | Other bodies stop at it |
| `bounce` | Fixed | `0` | 0 … 1 | Bounce: 0 stops, 1 comes back as fast |

Signals: `landed` (Touched the floor (data: falling speed in 1/16 pixel)), `collided` (Stopped at a solid body (data: its id))

### StaticBody2D

A body that does not move by itself and stops the others (wall, crate, moving platform).

Made with: `new_static_body2d(name, x, y)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `layer` | Int | `1` | 0 … 65535 | Layers it is in (bits) |

### Area2D

A zone that tells who comes in and goes out; it does not push.

Made with: `new_area2d(name, x, y)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `layer` | Int | `1` | 0 … 65535 | Layers it is in |
| `mask` | Int | `1` | 0 … 65535 | Layers of what it sees |
| `monitoring` | Bool | true |  | Watches who comes in |

Signals: `body_entered` (A body came in (data: its id)), `body_exited` (A body went out), `area_entered` (Another area came in), `area_exited` (Another area went out)

### TileMap

A map of Forja's map editor (.fmap): its layers are painted on the background; the collision layer stops bodies.

Made with: `new_tilemap(name, file)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `file` | Map | — |  | .fmap file |
| `tileset` | Image | — |  | Another tileset (if not, the map's) |
| `iso` | Bool | false |  | Isometric: diamond tiles |
| `spawn` | Spawn | `{}` |  | Kind of map object -> scene put in its place |

### Camera2D

The camera: follows a node, a screen at a time, within its limits.

Made with: `new_camera2d(name)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `target` | NodePath | — |  | Path of the node it follows |
| `limits` | Limits | `"map"` |  | Size of the world, or "map": the first map's |

### Label

A text. With bg >= 0 it is painted on the background only when it changes (cheap).

Made with: `new_label(name, x, y, text, pen, bg)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `text` | String | — |  | The text |
| `pen` | Color | `1` | 0 … 255 | Text colour |
| `bg` | Color | `0` | -1 … 255 | Box colour (-1: on top every frame) |
| `bind` | String | — |  | Game variable it shows |
| `prefix` | String | — |  | Text before the value |

### Timer

Says timeout after a while, once or again and again.

Made with: `new_timer(name, wait, one_shot)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `wait` | Int | `50` | 1 … 100000 | Video frames (50 are a second) |
| `one_shot` | Bool | false |  | Once |
| `autostart` | Bool | false |  | Starts when it enters the tree |

Signals: `timeout` (The time went by)

### AudioPlayer

A sound effect (8SVX): play() sounds it.

Made with: `new_audio(name, file, channel)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `file` | Sound | — |  | 8SVX file |
| `channel` | Int | `-1` | -1 … 3 | Channel 0 to 3 (-1: the first free one) |
| `volume` | Int | `64` | 0 … 64 | Volume |

### Particles2D

A few dots that fly and fall (sparks, dust): start() lets them go.

Made with: `new_particles2d(name, x, y, amount, pen)`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `amount` | Int | `8` | 1 … 64 | How many |
| `pen` | Color | `1` | 0 … 255 | Colour |
| `lifetime` | Int | `25` | 1 … 500 | Frames they last |
| `speed` | Int | `24` | 0 … 256 | Speed (1/16 pixel) |
| `gravity` | Int | `2` | -32 … 32 | Gravity (1/16 pixel) |
| `size` | Int | `2` | 1 … 8 | Side of each dot |
| `one_shot` | Bool | true |  | Once per start() |

## Ready-made behaviours

### Platformer

Runs and jumps with gravity (arrows or joystick, space or fire). Plays the animations idle, walk and jump (and _left).

`n.add_behavior(Platformer())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `speed` | Fixed | `2` | 0 … 16 | Top speed |
| `accel` | Fixed | `0.25` | 0 … 4 | Acceleration a step |
| `friction` | Fixed | `0.3` | 0 … 4 | Braking without input |
| `gravity` | Fixed | `0.35` | 0 … 4 | Gravity |
| `max_fall` | Fixed | `6` | 0 … 16 | Top falling speed |
| `jump` | Fixed | `5.5` | 0 … 16 | Jump speed |
| `jumps` | Int | `1` | 0 … 5 | Jumps in a row (2: double jump) |
| `player` | Bool | true |  | Moved by the player (if not, dir and want_jump) |

Signals: `jumped` (Jumped)

### EightWay

Moves in eight directions (top-down view).

`n.add_behavior(EightWay())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `speed` | Fixed | `2` | 0 … 16 | Speed |
| `accel` | Fixed | `0.5` | 0 … 16 | Acceleration |
| `player` | Bool | true |  | Moved by the player |

### Bullet

Goes straight; with a body, it goes when it hits a wall.

`n.add_behavior(Bullet())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `vx` | Fixed | `4` | -16 … 16 | Speed x |
| `vy` | Fixed | `0` | -16 … 16 | Speed y |
| `destroy_on_wall` | Bool | true |  | Goes when it hits |

### Follow

Goes towards another node (by path or "group:name").

`n.add_behavior(Follow())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `target` | NodePath | `"/Player"` |  | Path or group of the one it follows |
| `speed` | Fixed | `1` | 0 … 16 | Speed |
| `distance` | Int | `0` | 0 … 320 | Stops at this distance |
| `only_x` | Bool | false |  | Only in x (a rival in a race) |

### Patrol

Walks one way and turns at walls and edges.

`n.add_behavior(Patrol())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `speed` | Fixed | `0.75` | 0 … 8 | Speed |
| `dir` | Int | `-1` | -1 … 1 | Direction at the start |
| `gravity` | Fixed | `0.35` | 0 … 4 | Gravity (0: flies) |
| `turn_at_edges` | Bool | true |  | Turns at the edges of the floor |

### BounceEdges

Bounces off the edges of the world (Pong's ball).

`n.add_behavior(BounceEdges())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `vx` | Fixed | `2` | -16 … 16 | Speed x |
| `vy` | Fixed | `2` | -16 … 16 | Speed y |
| `left` | Bool | true |  | Bounces left |
| `right` | Bool | true |  | Bounces right |
| `top` | Bool | true |  | Bounces at the top |
| `bottom` | Bool | true |  | Bounces at the bottom |

Signals: `bounced` (Bounced (data: 0 in x, 1 in y))

### Wrap

Goes out one side of the world and in by the other.

`n.add_behavior(Wrap())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `margin` | Int | `0` | 0 … 320 | Margin |

### DestroyOffscreen

Goes when it leaves the world.

`n.add_behavior(DestroyOffscreen())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `margin` | Int | `32` | 0 … 320 | Margin |

Signals: `left_world` (Left the world)

### Health

Life: hears "damage" and "heal"; blinks after a hit.

`n.add_behavior(Health())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `hp` | Int | `3` | 1 … 1000 | Life points |
| `max_hp` | Int | `3` | 1 … 1000 | Maximum life |
| `invulnerable` | Int | `50` | 0 … 500 | Frames without damage after a hit |
| `destroy` | Bool | true |  | Goes when it dies |
| `var_name` | String | — |  | Game variable with the life |

Signals: `hurt` (Was hurt (data: life left)), `died` (Ran out of life)

### Damage

Hurts the ones of the group it touches.

`n.add_behavior(Damage())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `group` | String | `"player"` |  | Group it hurts |
| `amount` | Int | `1` | 1 … 1000 | Damage |
| `destroy_self` | Bool | false |  | Goes when it hurts (a bullet) |

### Pickup

Picked up: adds to a variable, sounds and goes.

`n.add_behavior(Pickup())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `group` | String | `"player"` |  | Group that picks it up |
| `var_name` | String | `"score"` |  | Game variable |
| `amount` | Int | `1` | -1000 … 1000 | How much it adds |
| `sound` | Sound | — |  | Sound when picked up |

Signals: `picked` (Picked up (data: id of who))

### Draggable

The mouse drags it.

`n.add_behavior(Draggable())`

Signals: `drag_started` (Started being dragged), `dropped` (Was dropped)

### Blink

Blinks for a while or always.

`n.add_behavior(Blink())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `period` | Int | `8` | 1 … 100 | Frames on and off |
| `duration` | Int | `0` | 0 … 10000 | How long (0: always) |

Signals: `blink_finished` (Stopped blinking)

### Vehicle

Side-view car or motorbike: accelerates, brakes, inertia, gears, jumps; tells when it lands too fast.

`n.add_behavior(Vehicle())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `accel` | Fixed | `0.08` | 0 … 2 | Acceleration a step |
| `brake` | Fixed | `0.2` | 0 … 2 | Braking |
| `drag` | Fixed | `0.02` | 0 … 2 | Drag without input |
| `gears` | Int | `3` | 1 … 6 | Gears |
| `gear_speed` | Fixed | `1.5` | 0 … 8 | Top speed per gear |
| `gravity` | Fixed | `0.3` | 0 … 4 | Gravity |
| `jump` | Fixed | `5` | 0 … 16 | Jump speed |
| `crash_speed` | Int | `96` | 0 … 512 | Falling speed that crashes (1/16 pixel) |
| `player` | Bool | true |  | Driven by the player |

Signals: `gear` (Changed gear (data: the gear)), `jumped` (Jumped), `crashed` (Landed too fast (data: speed))

### Sine

Goes up and down (or to and fro) around where it started.

`n.add_behavior(Sine())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `amplitude` | Int | `8` | 0 … 320 | How far it goes (pixels) |
| `period` | Int | `100` | 2 … 10000 | Frames a turn |
| `horizontal` | Bool | false |  | To and fro in x |

### Shooter

Emits "shoot" every so often or when an action is pressed; an event makes the bullet (spawn action).

`n.add_behavior(Shooter())`

| Property | Type | Default | Range | What it is |
|---|---|---|---|---|
| `every` | Int | `25` | 1 … 1000 | Frames between shots |
| `action` | String | — |  | Action that shoots (empty: by itself) |

Signals: `shoot` (Time to shoot)

## Event actions

| `do` | What it is | Code |
|---|---|---|
| `add` | Adds to a game variable | `game_add(VAR, VALUE)` |
| `set` | Sets a game variable | `game_set(VAR, VALUE)` |
| `sound` | Plays a sound effect | `play_sound(FILE)` |
| `music` | Starts a MOD music | `play_music(FILE)` |
| `destroy` | Removes this node (or the other) | `n.queue_free()` |
| `emit` | Emits a signal | `n.emit(SIGNAL, DATA)` |
| `damage` | Hurts the other one | `send_signal(other, "damage", n, VALUE)` |
| `spawn` | Puts a copy of another scene next to this node | `spawn(n, scene_X(), X, Y)` |
| `play` | Plays an animation | `n.get_node(TARGET).play(ANIM)` |
| `start` | Starts a Timer or particles | `n.get_node(TARGET).start()` |
| `show` | Shows it | `n.visible = true` |
| `hide` | Hides it | `n.visible = false` |
| `change_scene` | Changes the scene | `change_scene(scene_X())` |
| `quit` | Ends the game | `quit()` |
| `code` | Hand-written Dash | `DASH` |
