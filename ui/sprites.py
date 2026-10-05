"""Pixel-art sprites defined as code (same result as pyxel edit, testable).

Each sprite is 16x16, chars are palette colors (0-9, a-f; '.' = transparent).
Loaded into image bank 0 at the offsets in SLOTS. Drawing code uses
blt() and falls back to primitives when sprites are unavailable.
"""
SIZE = 16

HERO = [
    "................",
    "......ffff......",
    ".....fbbbbf.....",
    ".....bfbbbf.....",
    ".....fbbbbf.....",
    "......ffff......",
    "....ffffffff....",
    "...fbbbbbbbbf...",
    "...fbfffffff....",
    "...fbfbbbfbf....",
    "....fffffff.....",
    "....fbb.fbb.....",
    "....fbb.fbb.....",
    "....fff.fff.....",
    "................",
    "................",
]

SKELETON = [
    "................",
    ".....777777.....",
    "....77777777....",
    "....70777707....",
    "....77777777....",
    ".....777777.....",
    "......7777......",
    "...7777777777...",
    "..770777777077..",
    "..777777777777..",
    "....77777777....",
    "....777..777....",
    "....777..777....",
    "....777..777....",
    "................",
    "................",
]

SKULL = [
    "....77777777....",
    "..777777777777..",
    ".77777777777777.",
    ".77007777770077.",
    ".77007777770077.",
    ".77777777777777.",
    "..777777777777..",
    "..777700007777..",
    "...7770000777...",
    "...7777777777...",
    "....70707070....",
    "....77777777....",
    "................",
    "................",
    "................",
    "................",
]

SLOTS = {"hero": (0, 0), "enemy": (16, 0), "boss": (32, 0)}

SPRITES = {"hero": HERO, "enemy": SKELETON, "boss": SKULL}


def load_into_bank(images):
    """Copy sprite maps into image bank 0 ('.' = transparent, else hex)."""
    bank = images[0]
    for name, rows in SPRITES.items():
        ox, oy = SLOTS[name]
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch == ".":
                    continue
                bank.pset(ox + dx, oy + dy, int(ch, 16))
    return True


def draw(images_blt, name, x, y):
    """Thin wrapper so game code has one call site (blt with colkey)."""
    ox, oy = SLOTS[name]
    images_blt(int(x), int(y), 0, ox, oy, SIZE, SIZE, 0)
