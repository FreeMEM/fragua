# Fragua

A library for making games in [Dash](https://github.com/FreeMEM/dash) on the Amiga. It comes in two layers: loose
pieces, as in pygame, and a tree of nodes and scenes, as in Godot. The design is in `docs/JUEGOS_DISENO.md` of
[Forja](https://github.com/FreeMEM/forja). The API is in English, like Dash's builtins.

Status: **phase 1**, the layer of loose pieces, with a Pong example. The node layer comes later.

[Español](README.md)

## Requirements

A Dash with `key_down`, `bob_paste` and `bob_width`, `bob_height` and `bob_frames`. The base machine is an A1200;
on an A500 it works with fewer things on screen.

## Use

```
import "fragua/fragua.dash"

Main
    s = screen_open(320, 256, 5, "My game")
    s.background(0)
    ship = sprite_new(image_load("ship.iff"), 160, 200)
    clock = clock_new(50)
    while not key(KEY_ESC)
        n = clock.tick()
        s.begin()
        ship.erase()
        ship.rect.x = ship.rect.x + axis_x(1) * 2 * n
        ship.draw()
        s.present()
    end
    s.close()
end
```

- **Screen** (`screen_open`): a screen of its own, double buffered. `color`, `palette` (an IFF's colours), `rect`,
  `text`, `present` (shows what was drawn at the next vertical blank).
- **Background:** clearing the whole screen costs more than a frame, so the screen keeps a background
  (`background`, or `background_start` ... `background_end` to draw on it). Each frame starts with `s.begin()` and
  the sprites' `erase()`, which put the background back only where they were.
- **Image** (`image_load`, `image_new`): an IFF from Forja's sprite editor, with its frames, drawn with its mask
  (colour 0 transparent).
- **Rect:** collisions, intersection, union, `clamp`.
- **Clock** (`clock_new(50)`): `tick()` says how many frames went by (more than 1 if the game was late).
- **Input:** `key(KEY_ESC)` (a key held down now), `axis_x(1)`, `axis_y(1)` and `fire(1)` (joystick, or arrows and
  space).
- **Sprite and Group:** image, rectangle, frame and speed; the group moves, draws, erases and finds collisions.

## What it costs

Measured in FS-UAE at real speed (`bench/costes.sh`), 320x256 screen with 5 planes:

| | A1200 | A500 |
|---|---|---|
| Clear the whole screen | 36.7 ms | 37.4 ms |
| 16x16 image with mask | 1.6 ms | 3.3 ms |
| 32x32 image with mask | 3.5 ms | 5.4 ms |
| 32x32 rectangle | 0.9 ms | 1.2 ms |
| 13-letter text | 2 ms | 4.6 ms |
| `key_down` | 0.08 ms | 0.28 ms |
| `Rect.collides` | 0.02 ms | 0.13 ms |

A frame is 20 ms. The Pong example spends 5 ms a frame on an A1200 (it loses 2 of 500, drawing the background at
the start) and 15 ms on an A500 (it loses 90 of 500).

## Examples and tests

- `examples/pong/pong.dash`: W and S, or the joystick; the right paddle plays by itself. Esc quits.

  ![The Pong example](examples/pong/pong.png)

- `tests/todas.sh DASH_DIR`: the `Rect` test and Pong in demo mode (`ENV:FRAGUA_DEMO`: it plays by itself for 500
  frames), in FS-UAE with `DASH_KICKSTART` (3.1). `REAL=1 tests/pong.sh ...` at the speed of an A1200; `A500=1`,
  of an A500.

## To do

- Faster masked drawing: the system's masked blit (`BltMaskBitMapRastPort`) makes several blitter passes a plane.
  Driving the blitter directly (with `OwnBlitter`) would do it in one.
- `key_down` has not been tried with a real key: the test emulator only simulates keys through `input.device`,
  which does not reach the keyboard's matrix.
- Phase 2: tile maps (from Forja's map editor) and a camera with hardware scrolling.
