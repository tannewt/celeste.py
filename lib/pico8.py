import _stage
import array
import math
import random
import gc

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
    ss_buffer = bytearray(4 * 8 * 16 * 16)
    for row in range(128):
        data = f.readline().strip()
        for col in range(64):
            i = row * 64 + col
            ss_buffer[i] = int(data[2 * col + 1], 16) << 4 | int(data[2 * col], 16)
    sprite_sheet = _stage.SpriteSheet(ss_buffer, 16, 16, bits_per_pixel=4, sprite_width=8, sprite_height=8)

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
    celx = int(celx)
    cely = int(cely)
    return tile_map[128 * cely + celx]


def pal(c0=None, c1=None, p=0):
    pass

def rectfill(x0, y0, x1, y1, col=None):
    pass

def circfill(x, y, r, col=None):
    pass

maps = {}
layers = []
layer_x = {}
layer_y = {}
_buffer = bytearray(320*2*2*4)
buttons = 0
min_x = 128
max_x = 0
min_y = 120
max_y = 0

def btn(i, p=0):
    #print("btn", i, p)
    return p == 0 and (buttons & (1 << i)) != 0

def _map(celx, cely, sx, sy, celw, celh, layer=0):
    global min_x, min_y, max_x, max_y
    x = -8*celx + sx
    y = -8*cely + sy - 4
    if layer not in maps:
        maps[layer] = _stage.Layer(128, 64, sprite_sheet, palette, tile_map)

    #print("_map", layer, celx, cely, sx, sy, celw, celh)

    if layer not in layer_x or layer_x[layer] != x or layer_y[layer] != y:
        maps[layer].move(x, y)
        layer_x[layer] = x
        layer_y[layer] = y
        min_x = 0
        max_x = 128
        min_y = 0
        max_y = 120
    if layer != 8:
        layers.append(maps[layer])

sprites = {}
last_dim = (0, 0, 128, 120)

def tick(display, button_state):
    global layers, sprites, buttons, min_x, min_y, max_x, max_y, last_dim
    dim = (min_x, min_y, max_x, max_y)
    # If we have new dimensions then combine our frames with the previous
    if last_dim != dim:
        min_x = min(min_x, last_dim[0])
        min_y = min(min_y, last_dim[1])
        max_x = max(max_x, last_dim[2])
        max_y = max(max_y, last_dim[3])
    min_x = max(min_x, 0)
    min_y = max(min_y, 0)
    max_x = min(max_x, 128)
    max_y = min(max_y, 120)
    #print(min_x, min_y, max_x, max_y)
    last_dim = dim
    buttons = button_state
    #print(buttons)
    if min_x < max_x:
        display.block(min_x, min_y, max_x, max_y)
        while not display.spi.try_lock():
            pass
        display.spi.configure(baudrate=24000000, polarity=0, phase=0)

        display.cs.value = False
        # TODO(tannewt): Reverse the layer list automatically
        layers = list(reversed(layers))

        #print(layers)
        _stage.render(min_x, min_y, max_x, max_y, layers, _buffer, display.spi, 2)
        display.cs.value = True
        display.spi.unlock()
    # Reset the window
    min_x = 128
    max_x = 0
    min_y = 120
    max_y = 0
    layers = []
    # Throw sprites away for now
    sprites = {}
    #gc.collect()
    #print("mem free", gc.mem_free())

def spr(n, x, y, w=1.0, h=1.0, flip_x=False, flip_y=False):
    global min_x, min_y, max_x, max_y
    n = int(n)
    #print("spr", n, x, y, w, h, flip_x, flip_y)
    if n not in sprites:
        sprites[n] = _stage.Layer(1, 1, sprite_sheet, palette)
    x = int(x)
    y = int(y)
    sprites[n].move(x, y - 4)
    sprites[n].frame(n, flip_x=flip_x, flip_y=flip_y)
    min_x = min(min_x, x)
    max_x = max(max_x, x + 8)
    min_y = min(min_y, y - 4)
    max_y = max(max_y, y + 4)
    layers.append(sprites[n])

def _print(s, x=None, y=None, col=None):
    pass

def sfx(n, channel=-1, offset=0, length=None):
    pass

flr = math.floor

def rnd(end):
    return random.uniform(0, end)

def camera(x=0, y=0):
    pass

def fget(n, f=0xff):
    if f != 0xff:
        f = 1 << f
    flags = 0x0
    if 32 <= n <= 39 or 48 <= n <= 55 or n in (64, 65, 80, 81):
        flags = 3
    #print("fget", n, f, (flags & f) != 0)
    return (flags & f) != 0
