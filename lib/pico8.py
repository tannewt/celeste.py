import _stage
import array
import math

sprite_sheet = None
tile_map = None
ss_buffer = None
default_palette = [0x0000, #000000
                   0x4351, #1d2b53
                   0x2f51, #7e2553
                   0x2054, #008751
                   0x9532, #ab5236
                   0xab4a, #5f574f
                   0x18c6, #c2c3c7
                   0x9fef, #fff1e8
                   0x1f48, #ff004d
                   0x1f05, #ffa300
                   0x7f27, #ffec27
                   0x2037, #00e436
                   0x65fd, #29adff
                   0xb09b, #83769c
                   0xbfab, #ff77a8
                   0x7fae, #ffccaa
]
palette = array.array("H", default_palette)

def find_section(f, header):
    f.seek(0)
    next_line = f.readline()
    while next_line and next_line != header:
        next_line = f.readline()

def load_gfx(f):
    global sprite_sheet, ss_buffer
    find_section(f, "__gfx__\n")
    ss_buffer = bytearray(4 * 8 * 16 * 32)
    for row in range(128):
        data = f.readline().strip()
        for col in range(64):
            i = row * 64 + col
            ss_buffer[i] = int(data[2 * col + 1], 16) << 4 | int(data[2 * col], 16)
    sprite_sheet = _stage.SpriteSheet(ss_buffer, 16, 32, bits_per_pixel=4, sprite_width=8, sprite_height=8)

def load_map(f):
    global tile_map
    find_section(f, "__map__\n")
    tile_map = bytearray(128 * 64)
    for row in range(32):
        data = f.readline().strip()
        for col in range(128):
            i = row * 128 + col
            tile_map[i] = int(data[2 * col], 16) << 4 | int(data[2 * col + 1], 16)
    # Copy the latter half of the sprite into the map in case its used.
    tile_map[128*32:] = ss_buffer[128 * 32:]

def load_resources(filename):
    palette = array.array("H", default_palette)
    with open(filename, "r") as f:
        if f.readline() != "pico-8 cartridge // http://www.pico-8.com\n":
            raise ValueError("File not valid pico-8 cartridge")
        version = f.readline().strip().split()
        version = int(version[1])
        if version != 16:
            print("Unknown version, may not work")

        load_gfx(f)
        load_map(f)

def music(n, fadems=0, channelmask=0):
    pass

def mget(celx, cely):
    return tile_map[128 * cely + celx]


def pal(c0=None, c1=None, p=0):
    pass

def rectfill(x0, y0, x1, y1, col=None):
    pass

def circfill(x, y, r, col=None):
    pass

maps = {}
layers = []
_buffer = bytearray(4096)
buttons = 0

def btn(i, p=0):
    print("btn", i, p)
    return p == 0 and (buttons & (1 << i)) != 0

def _map(celx, cely, sx, sy, celw, celh, layer=0):
    if layer not in maps:
        maps[layer] = _stage.Layer(128, 64, sprite_sheet, palette, tile_map)
    print(layer, celx, cely, sx, sy, celw, celh)
    maps[layer].move(-8*celx + sx,-8*cely + sy)
    if layer != 8:
        layers.append(maps[layer])

sprites = {}

def tick(display, button_state):
    global layers, sprites, buttons
    display.block(0, 0, 128, 120)
    while not display.spi.try_lock():
        pass
    display.spi.configure(baudrate=24000000, polarity=0, phase=0)

    buttons = button_state
    print(buttons)

    display.cs.value = False
    # TODO(tannewt): Reverse the layer list automatically
    layers = list(reversed(layers))
    print(layers)
    _stage.render(0, 0, 128, 120, layers, _buffer, display.spi, 2)
    display.cs.value = True
    display.spi.unlock()
    layers = []
    # Throw sprites away for now
    sprites = {}


def spr(n, x, y, w=1.0, h=1.0, flip_x=False, flip_y=False):
    if n not in sprites:
        sprites[n] = _stage.Layer(1, 1, sprite_sheet, palette)
    sprites[n].move(x, y)
    sprites[n].frame(8)
    layers.append(sprites[n])
    print("spr", n, x, y, w, h, flip_x, flip_y)

def _print(s, x=None, y=None, col=None):
    pass

def sfx(n, channel=-1, offset=0, length=None):
    pass

flr = math.floor

def rnd(end):
    return random.uniform(0, end-)
