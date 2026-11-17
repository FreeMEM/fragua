#!/usr/bin/env python3
"""Los recursos de los ejemplos de Fragua: imágenes IFF ILBM (como las del editor de sprites de Forja, con su trozo
FRJA), mapas .fmap (como los del editor de mapas de Forja) y sonidos 8SVX, hechos con código.

    python3 tools/recursos.py plataformas examples/plataformas    # el tileset, los sprites, el nivel y los sonidos
    python3 tools/recursos.py iso examples/iso                    # el tileset en rombo y el mapa isométrico

Solo usa la biblioteca estándar.
"""
import math
import os
import struct
import sys


# --- IFF ---

def trozo(tipo, datos):
    t = tipo.encode() + struct.pack(">I", len(datos)) + datos
    return t + (b"\0" if len(datos) & 1 else b"")


def ilbm(ruta, filas, paleta, planos, ancho_fotograma=None, velocidad=0):
    """filas: lista de filas de índices de color; los fotogramas uno al lado del otro"""
    alto = len(filas)
    ancho = len(filas[0])
    fila_bytes = (ancho + 15) // 16 * 2
    bmhd = struct.pack(">HHhhBBBBHBBhh", ancho, alto, 0, 0, planos, 2, 0, 0, 0, 10, 11, ancho, alto)
    cuerpo = bytearray()
    for y in range(alto):
        for p in range(planos):
            fila = bytearray(fila_bytes)
            for x in range(ancho):
                if (filas[y][x] >> p) & 1:
                    fila[x // 8] |= 0x80 >> (x % 8)
            cuerpo += fila
    cmap = b"".join(struct.pack(">BBB", *c) for c in paleta[:1 << planos])
    datos = b"ILBM" + trozo("BMHD", bmhd) + trozo("CMAP", cmap)
    if ancho_fotograma:
        datos += trozo("FRJA", ("1 0 %d %d" % (ancho_fotograma, velocidad)).encode())
    datos += trozo("BODY", bytes(cuerpo))
    with open(ruta, "wb") as f:
        f.write(b"FORM" + struct.pack(">I", len(datos)) + datos)


def fmap(ruta, ancho, alto, tile, tileset, capas, objetos=()):
    """capas: (nombre, tipo, celdas); objetos: (x, y, clase, nombre, sprite)"""
    trozos = [b"MHDR" + struct.pack(">I5H", 10, 1, ancho, alto, tile, len(capas))]
    t = tileset.encode("latin-1")
    trozos.append(b"TSET" + struct.pack(">I", len(t)) + t + (b"\0" if len(t) % 2 else b""))
    for nombre, tipo, celdas in capas:
        n = nombre.encode("latin-1")
        cab = bytes([tipo, 1, len(n)]) + n + (b"\0" if (3 + len(n)) % 2 else b"")
        datos = cab + struct.pack(">%dH" % (ancho * alto), *celdas)
        trozos.append(b"LAYR" + struct.pack(">I", len(datos)) + datos)
    if objetos:
        datos = struct.pack(">H", len(objetos))
        for x, y, clase, nombre, sprite in objetos:
            o = struct.pack(">hh", x, y)
            for s in (clase, nombre, sprite):
                s = s.encode("latin-1")
                o += bytes([len(s)]) + s
            datos += o + (b"\0" if len(o) % 2 else b"")
        trozos.append(b"OBJS" + struct.pack(">I", len(datos)) + datos)
    cuerpo = b"FMAP" + b"".join(trozos)
    with open(ruta, "wb") as f:
        f.write(b"FORM" + struct.pack(">I", len(cuerpo)) + cuerpo)


def svx(ruta, muestras, frecuencia):
    vhdr = struct.pack(">IIIHBBi", len(muestras), 0, 0, frecuencia, 1, 0, 0x10000)
    body = bytes((m + 256) % 256 for m in muestras)
    datos = b"8SVX" + trozo("VHDR", vhdr) + trozo("BODY", body)
    with open(ruta, "wb") as f:
        f.write(b"FORM" + struct.pack(">I", len(datos)) + datos)


# --- dibujar en una rejilla ---

def lienzo(w, h, c=0):
    return [[c] * w for _ in range(h)]


def rect(img, x, y, w, h, c):
    for j in range(y, y + h):
        for i in range(x, x + w):
            if 0 <= j < len(img) and 0 <= i < len(img[0]):
                img[j][i] = c


def pinta(img, x0, y0, dibujo, colores):
    """dibujo: líneas de caracteres; colores: carácter -> índice ('.' transparente)"""
    for j, linea in enumerate(dibujo):
        for i, ch in enumerate(linea):
            if ch in colores:
                img[y0 + j][x0 + i] = colores[ch]


def tira(fotogramas):
    """los fotogramas (rejillas del mismo alto) uno al lado del otro"""
    alto = len(fotogramas[0])
    return [sum((f[y] for f in fotogramas), []) for y in range(alto)]


# --- la paleta de los ejemplos (32 colores) ---

PALETA = [
    (20, 24, 46),     # 0 fondo: azul noche
    (240, 240, 232),  # 1 blanco
    (16, 16, 20),     # 2 negro
    (90, 160, 230),   # 3 cielo
    (60, 120, 200),   # 4 cielo oscuro
    (70, 170, 70),    # 5 hierba
    (40, 120, 50),    # 6 hierba oscura
    (150, 100, 60),   # 7 tierra
    (110, 70, 40),    # 8 tierra oscura
    (190, 80, 60),    # 9 ladrillo
    (130, 50, 40),    # 10 ladrillo oscuro
    (200, 170, 110),  # 11 madera
    (140, 110, 70),   # 12 madera oscura
    (250, 210, 60),   # 13 oro
    (200, 140, 30),   # 14 oro oscuro
    (230, 70, 70),    # 15 rojo
    (250, 200, 160),  # 16 piel
    (50, 90, 200),    # 17 azul
    (30, 50, 130),    # 18 azul oscuro
    (160, 60, 170),   # 19 morado
    (100, 30, 110),   # 20 morado oscuro
    (180, 180, 190),  # 21 gris claro
    (110, 110, 120),  # 22 gris
    (70, 70, 80),     # 23 gris oscuro
    (230, 120, 40),   # 24 naranja
    (130, 200, 240),  # 25 celeste
    (60, 140, 140),   # 26 verde azulado
    (40, 90, 90),     # 27 verde azulado oscuro
    (250, 250, 140),  # 28 amarillo claro
    (90, 60, 120),    # 29 lila oscuro
    (200, 220, 255),  # 30 nube
    (255, 255, 255),  # 31 blanco puro
]


# --- plataformas ---

def tiles_plataformas():
    t = []
    # 1 suelo con hierba
    a = lienzo(16, 16, 7)
    rect(a, 0, 0, 16, 4, 5)
    rect(a, 0, 4, 16, 1, 6)
    for i in range(0, 16, 3):
        a[5 + (i % 4)][i] = 8
        a[11 - (i % 5)][(i + 7) % 16] = 8
    for i in range(0, 16, 2):
        a[0][i] = 6
    t.append(a)
    # 2 tierra
    a = lienzo(16, 16, 7)
    for i in range(0, 16, 3):
        a[(i * 5) % 16][i] = 8
        a[(i * 7 + 3) % 16][(i + 5) % 16] = 8
    t.append(a)
    # 3 ladrillo
    a = lienzo(16, 16, 9)
    for y in (0, 8):
        rect(a, 0, y, 16, 1, 10)
    for y, x in ((0, 0), (0, 8), (8, 4), (8, 12)):
        rect(a, x, y, 1, 8, 10)
    rect(a, 0, 0, 16, 1, 15)
    t.append(a)
    # 4 tablón (plataforma)
    a = lienzo(16, 16, 0)
    rect(a, 0, 0, 16, 5, 11)
    rect(a, 0, 4, 16, 1, 12)
    rect(a, 3, 5, 2, 4, 12)
    rect(a, 11, 5, 2, 4, 12)
    t.append(a)
    # 5 pendiente que sube (/) y 6 que baja (\)
    for sube in (True, False):
        a = lienzo(16, 16, 0)
        for x in range(16):
            alto = x + 1 if sube else 16 - x
            for y in range(16 - alto, 16):
                a[y][x] = 7
            top = 16 - alto
            a[top][x] = 5
            if top + 1 < 16:
                a[top + 1][x] = 5
            if top + 2 < 16:
                a[top + 2][x] = 6
        t.append(a)
    # 7 pinchos
    a = lienzo(16, 16, 0)
    for k in range(4):
        for j in range(8):
            for i in range(-(j // 2), j // 2 + 1):
                x = k * 4 + 2 + i
                if 0 <= x < 16:
                    a[8 + j][x] = 21 if i < 0 else 22
    t.append(a)
    # 8 nube (decorado)
    a = lienzo(16, 16, 0)
    for y in range(16):
        for x in range(16):
            if (x - 8) ** 2 / 64 + (y - 10) ** 2 / 20 < 1 or (x - 6) ** 2 + (y - 6) ** 2 < 14:
                a[y][x] = 30
    t.append(a)
    # 9 arbusto (decorado)
    a = lienzo(16, 16, 0)
    for y in range(16):
        for x in range(16):
            if (x - 8) ** 2 / 60 + (y - 13) ** 2 / 30 < 1:
                a[y][x] = 6 if (x + y) % 5 == 0 else 5
    t.append(a)
    return t


def personaje(fot):
    """el jugador: 16 x 16; fot 0 quieto, 1 y 2 andando, 3 saltando"""
    a = lienzo(16, 16)
    pinta(a, 0, 0, [
        ".....RRRRR......",
        "....RRRRRRRR....",
        "....HHHSSHS.....",
        "...HSHSSSHSSS...",
        "...HSHHSSSHSSS..",
        "...HHSSSSHHHH...",
        ".....SSSSSSS....",
        "....RRBRRR......",
        "...RRRBRRBRRR...",
        "..RRRRBBBBRRRR..",
        "..SSRBYBBYBRSS..",
        "..SSSBBBBBBSSS..",
        "..SSBBBBBBBBSS..",
    ], {"R": 15, "H": 8, "S": 16, "B": 17, "Y": 13})
    piernas = {
        0: ["....BBB..BBB....", "...HHH....HHH...", "..HHHH....HHHH.."],
        1: ["....BBB.BBB.....", "...HHH...HHH....", "........HHHH...."],
        2: [".....BBBBB......", "....HHHHHH......", "...HHHH........."],
        3: ["...BBB....BBB...", "..HHH......HHH..", ".HHH........HHH."],
    }[fot]
    pinta(a, 0, 13, piernas, {"B": 17, "H": 8})
    if fot == 3:
        rect(a, 0, 8, 2, 2, 16)
        rect(a, 14, 8, 2, 2, 16)
    return a


def enemigo(fot):
    a = lienzo(16, 16)
    for y in range(4, 16):
        for x in range(16):
            if (x - 7.5) ** 2 / 60 + (y - 11) ** 2 / 36 < 1:
                a[y][x] = 19 if y < 13 else 20
    rect(a, 4, 7, 3, 3, 1)
    rect(a, 9, 7, 3, 3, 1)
    rect(a, 5 + fot, 8, 1, 2, 2)
    rect(a, 10 + fot, 8, 1, 2, 2)
    if fot == 0:
        rect(a, 2, 15, 4, 1, 2)
        rect(a, 10, 15, 4, 1, 2)
    else:
        rect(a, 4, 15, 4, 1, 2)
        rect(a, 8, 15, 4, 1, 2)
    return a


def moneda(fot):
    a = lienzo(16, 16)
    ancho = [6, 4, 1, 4][fot]
    for y in range(16):
        for x in range(16):
            dx = (x - 7.5) / max(ancho, 0.8)
            dy = (y - 7.5) / 6.5
            if dx * dx + dy * dy < 1:
                a[y][x] = 13 if dx < 0.3 else 14
    if ancho > 2:
        rect(a, 7, 4, 1, 7, 28)
    return a


NIVEL = [
    "............................................................",
    "........ccc............................ccc....c.c.c.........",
    "..##...........ccc......................................ccc.",
    "...............====..........................=====.........",
    "...............................c.c..........................",
    "......ccc...................BBBBBB..................c.......",
    ".....=====.......................................#####......",
    "..........................................cc.....#####......",
    "..................c.....E..............==........#####...E..",
    "............c.c..===...BBBB...........................######",
    "......b.................................................####",
    "..P.............E....../##\\.......E.....b.......E......#####",
    "####################..######^^^#########...######/#########.",
    "####################..##########################//##########",
    "############################################################",
]
NIVEL[0] = "..n.........n..................n...........n...........n...."


def nivel_plataformas():
    alto = len(NIVEL)
    ancho = 60
    deco = [0] * (ancho * alto)
    tiles = [0] * (ancho * alto)
    choques = [0] * (ancho * alto)
    objetos = []
    filas = [f.ljust(ancho, ".")[:ancho] for f in NIVEL]
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            i = y * ancho + x
            if ch == "#":
                arriba = filas[y - 1][x] if y > 0 else "."
                tiles[i] = 2 if arriba in "#B/\\" else 1
                choques[i] = 1
            elif ch == "B":
                tiles[i] = 3
                choques[i] = 1
            elif ch == "=":
                tiles[i] = 4
                choques[i] = 2
            elif ch == "/":
                tiles[i] = 5
                choques[i] = 5
            elif ch == "\\":
                tiles[i] = 6
                choques[i] = 6
            elif ch == "^":
                tiles[i] = 7
                choques[i] = 4
            elif ch == "n":
                deco[i] = 8
            elif ch == "b":
                deco[i] = 9
            elif ch == "P":
                objetos.append((x * 16, y * 16, "player", "Jugador", ""))
            elif ch == "E":
                objetos.append((x * 16, y * 16, "enemy", "Enemigo", ""))
            elif ch == "c" and (x + y) % 2 == 0:      # one of each two: an A1200 draws about ten BOBs a frame
                objetos.append((x * 16, y * 16, "coin", "Moneda", ""))
    return ancho, alto, [("fondo", 0, deco), ("suelo", 0, tiles), ("choques", 1, choques)], objetos


def sonido_moneda():
    m = []
    for i in range(1800):
        f = 1400 if i < 600 else 2100
        v = 90 * (1 - i / 1800)
        m.append(int(v if (i * f // 8000) % 2 else -v))
    return m


def sonido_salto():
    m = []
    fase = 0.0
    for i in range(2400):
        f = 300 + i * 0.35
        fase += f / 8000
        v = 80 * (1 - i / 2400)
        m.append(int(v * (1 if fase % 1 < 0.5 else -1)))
    return m


def sonido_golpe():
    import random
    r = random.Random(3)
    return [int(r.randint(-100, 100) * (1 - i / 2000)) for i in range(2000)]


def espejo(img):
    return [list(reversed(f)) for f in img]


def plataformas(dir_):
    os.makedirs(dir_, exist_ok=True)
    ilbm(os.path.join(dir_, "tiles.iff"), tira(tiles_plataformas()), PALETA, 5, 16, 0)
    ilbm(os.path.join(dir_, "player.iff"), tira([personaje(i) for i in range(4)] + [espejo(personaje(i)) for i in range(4)]), PALETA, 5, 16, 6)
    ilbm(os.path.join(dir_, "enemy.iff"), tira([enemigo(i) for i in range(2)] + [espejo(enemigo(i)) for i in range(2)]), PALETA, 5, 16, 8)
    ilbm(os.path.join(dir_, "coin.iff"), tira([moneda(i) for i in range(4)]), PALETA, 5, 16, 6)
    ancho, alto, capas, objetos = nivel_plataformas()
    fmap(os.path.join(dir_, "level1.fmap"), ancho, alto, 16, "tiles.iff", capas, objetos)
    svx(os.path.join(dir_, "coin.8svx"), sonido_moneda(), 8000)
    svx(os.path.join(dir_, "jump.8svx"), sonido_salto(), 8000)
    svx(os.path.join(dir_, "hit.8svx"), sonido_golpe(), 8000)


# --- isométrico: tiles en rombo de 32 x 16 ---

def rombo(c1, c2, borde):
    a = lienzo(32, 16)
    for y in range(16):
        media = (y + 1) * 2 if y < 8 else (16 - y) * 2
        for x in range(16 - media, 16 + media):
            a[y][x] = c1 if x < 16 else c2
        a[y][16 - media] = borde
        a[y][16 + media - 1] = borde
    return a


def bloque():
    """un cubo de 32 x 32: la cara de arriba es un rombo, y dos lados"""
    a = lienzo(32, 32)
    top = rombo(21, 21, 22)
    for y in range(16):
        for x in range(32):
            if top[y][x]:
                a[y][x] = top[y][x]
    for y in range(8, 32):
        for x in range(32):
            if a[y][x] == 0:
                d = abs(x - 15.5)
                if y >= 8 + d / 2 and y < 24 + (16 - d) / 2:
                    a[y][x] = 22 if x < 16 else 23
    return a


def iso(dir_):
    os.makedirs(dir_, exist_ok=True)
    hierba = rombo(5, 6, 6)
    agua = rombo(17, 18, 18)
    arena = rombo(11, 12, 12)
    ilbm(os.path.join(dir_, "isotiles.iff"), tira([hierba, agua, arena]), PALETA, 5, 32, 0)
    ilbm(os.path.join(dir_, "block.iff"), bloque(), PALETA, 5, 32, 0)
    pj = lienzo(16, 24)
    pinta(pj, 0, 0, [
        "......RRRR......", ".....RRRRRR.....", ".....SSSSSS.....", ".....SBSSBS.....", ".....SSSSSS.....",
        "......SSSS......", "....BBBBBBBB....", "...BBBBBBBBBB...", "...SBBBBBBBBS...", "...SBBBBBBBBS...",
        "....BBBBBBBB....", "....HHH..HHH....", "....HHH..HHH....", "....HHH..HHH....", "...HHHH..HHHH...",
    ], {"R": 15, "S": 16, "B": 17, "H": 8})
    ilbm(os.path.join(dir_, "hero.iff"), pj, PALETA, 5, 16, 0)
    ancho = alto = 12
    suelo = [0] * (ancho * alto)
    choques = [0] * (ancho * alto)
    for y in range(alto):
        for x in range(ancho):
            v = 1
            if 2 <= x <= 4 and 6 <= y <= 9:
                v = 2
                choques[y * ancho + x] = 1
            elif x in (5, 6) and 5 <= y <= 10:
                v = 3
            suelo[y * ancho + x] = v
    objetos = [(1 * 16, 1 * 16, "player", "Heroe", "")]
    for (x, y) in ((8, 2), (9, 2), (8, 6), (3, 3), (10, 9)):
        objetos.append((x * 16, y * 16, "block", "Bloque", ""))
    fmap(os.path.join(dir_, "iso.fmap"), ancho, alto, 16, "isotiles.iff",
         [("suelo", 0, suelo), ("choques", 1, choques)], objetos)


if __name__ == "__main__":
    que, dir_ = sys.argv[1], sys.argv[2]
    {"plataformas": plataformas, "iso": iso}[que](dir_)
