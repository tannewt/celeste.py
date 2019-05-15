import array
import math
import random
import gc
import time

try:
    import gbio
    import adafruit_gameboy as platform
    from adafruit_gameboy import gb

    platform_id = "gb"

    if gbio.is_color():
        platform_id = "gbc"
except ImportError:
    import displayio as platform
    import adafruit_imageload
    import digitalio
    import board
    import gamepadshift
    platform_id = "adafruit"

sprite_sheet = None
tile_map = None
tile_map2 = None
ss_buffer = None
font = None
default_palette = [0x000000,
                   0x1d2b53,
                   0x7e2553,
                   0x008751,
                   0xab5236,
                   0x5f574f,
                   0xc2c3c7,
                   0xfff1e8,
                   0xff004d,
                   0xffa300,
                   0xffec27,
                   0x00e436,
                   0x29adff,
                   0x83769c,
                   0xff77a8,
                   0xffccaa
]

gameboy_color_mapping = [
    1,
    0,
    0,
    0,
    0,
    0,
    3,
    3,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2
]

if platform_id == "adafruit":
    single_color = [None]*16
    palette = platform.Palette(16)

    for i, color in enumerate(default_palette):
        palette[i] = color
        single_color[i] = platform.Palette(2)
        single_color[i].make_transparent(0)
        single_color[i][1] = color
    palette.make_transparent(0)

    gamepad = gamepadshift.GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                                        digitalio.DigitalInOut(board.BUTTON_OUT),
                                        digitalio.DigitalInOut(board.BUTTON_LATCH))

def find_section(f, header):
    f.seek(0)
    next_line = f.readline()
    while next_line and next_line != header:
        next_line = f.readline()

def load_gfx(f):
    global sprite_sheet, tile_map2
    first = True
    find_section(f, "__gfx__\n")
    tile_map2 = bytearray(64 * 64)
    if platform_id == "adafruit":
        sprite_sheet = platform.Bitmap(128, 128, 16)
        color_mapping = lambda x: x
    else:
        sprite_sheet = gb.tiles
        color_mapping = lambda x: gameboy_color_mapping[x]
        gb.tiles.auto_show = False
    data = bytearray(129)
    for row in range(128):
        f.readinto(data)
        t = time.monotonic()
        for col in range(128):
            i = row * 128 + col
            # Convert from ASCII hex to numeric value.
            value = data[col]
            if value >= 0x61:
                value = 10 + value - 0x61
            elif value >= 0x41:
                value = 10 + value - 0x41
            else:
                value -= 0x30

            if row > 64:
                i = (row - 64) * 64 + col // 2
                if col % 2 == 1:
                    tile_map2[i] += value << 4
                    # print(i, row // 2, col // 2, tile_map2[i], hex(tile_map2[i]))
                else:
                    tile_map2[i] = value
            else:
                sprite_sheet[i] = color_mapping(value)
        if row % 8 == 7 and (platform_id == "gb" or platform_id == "gbc"):
            if first:
                sprite_sheet.show()
        #print("row load", row, time.monotonic() - t)

def load_flags(f):
    global sprite_flags
    find_section(f, "__gff__\n")
    sprite_flags = bytearray(256)
    for row in range(2):
        data = f.readline().strip()
        for col in range(128):
            i = row * 128 + col
            sprite_flags[i] = int(data[2 * col], 16) << 4 | int(data[2 * col + 1], 16)

def load_map(f):
    global tile_map
    find_section(f, "__map__\n")
    if platform_id == "adafruit":
        tile_map = platform.Bitmap(128, 32, 256)
    else:
        tile_map = bytearray(128 * 32)
    for row in range(32):
        data = f.readline().strip()
        for col in range(128):
            i = row * 128 + col
            tile_map[i] = int(data[2 * col], 16) << 4 | int(data[2 * col + 1], 16)

def load_font():
    global font
    if platform_id == "adafruit":
        font, _ = adafruit_imageload.load("/pico8_font_packed.bmp", bitmap=platform.Bitmap)
        print(font)

def load_resources(filename):
    with open(filename, "r") as f:
        if f.readline() != "pico-8 cartridge // http://www.pico-8.com\n":
            raise ValueError("File not valid pico-8 cartridge")
        version = f.readline().strip().split()
        version = int(version[1])
        if version != 16:
            print("Unknown version, may not work")

        t = time.monotonic()
        load_gfx(f)
        print("gfx load", time.monotonic() - t)
        t = time.monotonic()
        load_map(f)
        print("map load", time.monotonic() - t)
        t = time.monotonic()
        load_flags(f)
        print("flags load", time.monotonic() - t)
        t = time.monotonic()

    load_font()

def music(n, fadems=0, channelmask=0):
    pass

def mget(celx, cely):
    celx = int(celx)
    cely = int(cely)
    if cely < 32:
        return tile_map[128 * cely + celx]
    else:
        index_y = 2 * cely + celx // 64
        i = (index_y * 64 + celx % 64) * 2
        return sprite_sheet[i] | sprite_sheet[i + 1] << 4

def pal(c0=None, c1=None, p=0):
    if platform_id == "adafruit":
        if c0 == None and c1 == None:
            for i, color in enumerate(default_palette):
                palette[i] = color
        else:
            palette[c0] = default_palette[c1]

def rectfill(x0, y0, x1, y1, col=None):
    pass

def circfill(x, y, r, col=None):
    pass

maps = {}
buttons = 0

def btn(i, p=0):
    #print("btn", i, p)
    return p == 0 and (buttons & (1 << i)) != 0

class _SpeedStub:
    def __init__(self):
        self.x = 0
        self.y = 0

class Map(platform.TileGrid):
    def __init__(self, bitmap, **kwargs):
        super().__init__(bitmap, **kwargs)
        self.spd = _SpeedStub()

    def move(self, dx, dy):
        pass

    def update(self):
        pass

def _map(celx, cely, sx, sy, celw=128, celh=32, layer_id=0):
    print(sprite_sheet)
    layer = Map(sprite_sheet, width=celw, height=celh, pixel_shader=palette, tile_width=8, tile_height=8)

    row_padding = 0
    if platform_id == "gb" or platform_id == "gbc":
        row_padding = 32 - celw

    print("_map", layer_id, celx, cely, sx, sy, celw, celh)
    layer.x = sx
    layer.y = sy

    for row in range(celw):
        y = row + cely
        for col in range(celh):
            x = col + celx
            if y > 31:
                i = (y - 32) * 128 + x
                tile_index = tile_map2[i]
            else:
                tile_index = tile_map[y * 128 + x]
            flags = sprite_flags[tile_index]
            if layer_id == 0 or flags & layer_id == layer_id:
                layer[row * (celw + row_padding) + col] = tile_index
            else:
                layer[row * (celw + row_padding) + col] = 0

    print("map done")
    return layer

sprites = {}
last_dim = (0, 0, 128, 120)
frame_count = 0
last_time = time.monotonic()
def tick(display, button_state):
    global layers, sprites, buttons, frame_count, last_dim, last_time
    #print("----------")
    this_time = time.monotonic()
    #print("frame:", frame_count, this_time - last_time)
    last_time = this_time

    # if True or frame_count > 77 and False:
    #     for i in range(10):
    #         display.wait_for_frame()
    # else:
    display.wait_for_frame()
    if platform_id == "gb" or platform_id == "gbc":
        buttons = ~gbio.get_pressed() & 0xff
        #print("buttons", buttons)
    else:
        buttons = gamepad.get_pressed()
        #print("buttons", hex(buttons))
    # if platform == "adafruit" and frame_count > 10:
    #     time.sleep(60)
    #     raise RuntimeError()

    frame_count += 1
    #gc.collect()
    # print("mem free", gc.mem_free())
    # print()

def spr(n, x, y, w=1.0, h=1.0, flip_x=False, flip_y=False):
    raise NotImplementedError("Please use a SpritePool to manage sprites")

def _print(s, x=None, y=None, color=0):
    if x is None or y is None:
        return
    if platform_id == "gb" or platform_id == "gbc":
        return
    if platform_id == "adafruit":
        return
    line_width = 0
    width = 0
    height = 1
    for c in s:
        if c == '\n':
            line_width = 0
            height += 1
        else:
            line_width += 1
            width = max(width, line_width)
    t = displayio.TileGrid(font, pixel_shader=single_color[color], tile_width=4, tile_height=6,
                           width=width, height=height, x=x+16, y=y)
    cursor_y_offset = 0
    cursor_x = 0
    for c in s:
        if c == '\n':
            cursor_y_offset += width
            cursor_x = 0
        else:
            o = ord(c)
            if o < 128:
                t[cursor_y_offset + cursor_x] = o - 0x20
                cursor_x += 1
            else:
                print(c, o)
                cursor_x += 2
    layers.append(t)
    return t

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
    flags = sprite_flags[n]
    #print("fget", n, f, (flags & f) != 0)
    return (flags & f) != 0
