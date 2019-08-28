import _gbio

class _SpeedStub:
    def __init__(self):
        self.x = 0
        self.y = 0

if _gbio.is_color():
    tile_to_colors = None

    TO_GBC = (
        b"\x00\x00" # 0 - 0x000000,
        b"\xa3\x28" # 1 - 0x1d2b53,
        b"\x8f\x28" # 2 - 0x7e2553,
        b"\x00\x2a" # 3 - 0x008751,
        b"\x55\x19" # 4 - 0xab5236,
        b"\x4b\x25" # 5 - 0x5f574f,
        b"\x18\x63" # 6 - 0xc2c3c7,
        b"\xdf\x77" # 7 - 0xfff1e8,
        b"\x1f\x24" # 8 - 0xff004d,
        b"\x9f\x02" # 9 - 0xffa300,
        b"\xbf\x13" # 10 - 0xffec27,
        b"\x80\x1b" # 11 - 0x00e436,
        b"\xa5\x7e" # 12 - 0x29adff,
        b"\xd0\x4d" # 13 - 0x83769c,
        b"\xdf\x55" # 14 - 0xff77a8,
        b"\x3f\x57" # 15 - 0xffccaa
    )

# # Use a function so we don't clutter the module with temporary vars
# def shrink_palette():
#     for i, color in enumerate(default_palette):
#         r = (color >> 16) & 0xff
#         g = (color >> 8) & 0xff
#         b = color & 0xff
#         packed = ((r >> 3) & 0x1f) | ((g >> 3) & 0x1f) << 5 | ((b >> 3) & 0x1f) << 10
#         print(i, hex(color), r, g, b, hex(packed))
# shrink_palette()

class PaletteTracker:
    def __init__(self, gb, is_sprite=False):
        self._gb = gb
        self._active_palettes = [None] * 8
        self._palette_refcount = [0] * 8
        self._is_sprite = is_sprite

    def free(self, index):
        self._palette_refcount[index] -= 1
        if self._palette_refcount[index] == 0:
            self._active_palettes[index] = None
        elif self._palette_refcount[index] < 0:
            raise RuntimeError("Extra free")

    def get(self, palette):
        for i, active in enumerate(self._active_palettes):
            if active == palette:
                return i
        return 0xff

    def alloc(self, palette):
        # First see if we already have it
        free_spot = None
        for i, active in enumerate(self._active_palettes):
            if active == palette:
                self._palette_refcount[i] += 1
                return i
            if active is None:
                free_spot = i

        if free_spot is None:
            raise RuntimeError("Too many palettes on one screen")

        print("alloc", free_spot, palette)

        # # Set the background palette
        offset = 0x80 + free_spot * 2 * 4
        if self._is_sprite:
            gb[0xff6a] = offset
            for color in palette:
                if color is None:
                    break
                self._gb[0xff6b] = TO_GBC[2 * color]
                self._gb[0xff6b] = TO_GBC[2 * color + 1]
        else:
            gb[0xff68] = offset
            for color in palette:
                if color is None:
                    break
                self._gb[0xff69] = TO_GBC[2 * color]
                self._gb[0xff69] = TO_GBC[2 * color + 1]

        self._active_palettes[free_spot] = palette
        self._palette_refcount[free_spot] = 1
        return free_spot

class Background:
    def __init__(self, gb):
        self._gb = gb
        self._x = 0
        self._y = 0
        self.spd = _SpeedStub()
        self._tile_to_palette = bytearray(32 * 32)
        # Use 0xff to represent unknown palette
        for i in range(32 * 32):
            self._tile_to_palette[i] = 0xff
        self._palette_tracker = PaletteTracker(gb, False)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._gb[0xff43] = 255 - value - 16

    @property
    def y(self):
        return self._y

    @x.setter
    def y(self, value):
        self._y = value
        self._gb[0xff42] = 255 - value

    def move(self, x, y):
        pass

    def update(self):
        pass

    def _show(self, indices):
        pass

    def _hide(self):
        pass

    # TODO: Add ability to clear screen and free all palettes at once

    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            index = index[0] * 32 + index[1]
        if _gbio.is_color():
            current_palette = self._tile_to_palette[index]
            palette = tile_to_colors[value]
            new_palette = self._palette_tracker.get(palette)
            if new_palette == 0xff or current_palette != new_palette:
                if current_palette < 0xff:
                    self._palette_tracker.free(current_palette)
                new_palette = self._palette_tracker.alloc(palette)
                self._tile_to_palette[index] = new_palette

                # Set the background tile options to it
                self._gb[0xff4f] = 0x1 # Set vram bank to 1
                self._gb[0x9800 + index] = new_palette
                self._gb[0xff4f] = 0x0 # Set vram bank to 0
                #print("swap palette", index, new_palette)
            #print("map index set", index, value, new_palette, palette)
        self._gb[0x9800 + index] = value

class AbsolutePositioner:
    def __init__(self, x=0, y=0):
        # These are coordinates in absolute gameboy screen space and can be modified by a parent's
        # coordinates changing.
        self.__absolute_x = 0
        self.__absolute_y = 0

        print("positioner init", self, "x", x, "y", y)

        self._x = None
        self._y = None

        # These are coordinates relative to the parent and are the normal CircuitPython API.
        self.x = x
        self.y = y

    @property
    def _absolute_x(self):
        return self.__absolute_x

    @_absolute_x.setter
    def _absolute_x(self, new_absolute_x):
        if self.__absolute_x == new_absolute_x:
            return
        self.__absolute_x = new_absolute_x
        self._update_x()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        if self._x == new_x:
            return
        self._x = new_x
        self._update_x()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        if self._y == new_y:
            return
        self._y = new_y
        self._update_y()

    @property
    def _absolute_y(self):
        return self.__absolute_y

    @_absolute_y.setter
    def _absolute_y(self, new_absolute_y):
        if self.__absolute_y == new_absolute_y:
            return
        self.__absolute_y = new_absolute_y
        self._update_y()

class TileGrid(AbsolutePositioner):
    def __init__(self, bitmap, *, pixel_shader, width=1, height=1, tile_height=8, tile_width=8, **kwargs):
        self._gb = gb
        self._width = width
        self._height = height
        self._oam_entries = [None] * (width * height)
        for i in range(width * height):
            self._oam_entries[i] = bytearray(4)
        self._oam_indices = [None] * (width * height)
        self._free_indices = None
        self._last_value = None
        super().__init__(**kwargs)

    def __setitem__(self, index, value):
        if self._oam_entries[index][2] == value:
            return
        palette_updated = False
        if _gbio.is_color() and self._oam_indices[index] is not None:
            attributes = self._oam_entries[index][3]
            old_palette_index = attributes & 0x7
            new_palette = tile_to_colors[value]
            pt = self._gb._sprite_palettes
            new_palette_index = pt.get(new_palette)
            if new_palette_index == 0xff or old_palette_index != new_palette_index:
                if old_palette_index < 0xff:
                    pt.free(old_palette_index)
                new_palette_index = pt.alloc(new_palette)
                self._oam_entries[index][3] = (attributes & 0xf8) | new_palette_index
                palette_updated = True

        print("map index set", self._oam_indices, index, value)
        self._oam_entries[index][2] = value
        if self._oam_indices[index] is not None:
            offset = self._compute_oam_address(index) + 2
            self._gb[offset] = value
            if palette_updated:
                self._gb[offset + 1] = self._oam_entries[index][3]

    def _update_x(self):
        value = int(self._absolute_x + self.x)
        # print("set sprite x", self, self._oam_indices, value)
        if self._last_value is not None and self._free_indices is not None and value - self._last_value == 16:
            raise RuntimeError()
        self._last_value = value
        for x in range(self._width):
            for y in range(self._height):
                i = x * self._height + y
                v = value + 8 * x + 8
                self._oam_entries[i][1] = v
                if self._oam_indices[i] is not None:
                    offset = self._compute_oam_address(i) + 1
                    self._gb[offset] = v

    def _update_y(self):
        value = int(self._absolute_y + self.y)
        # print("set sprite y", self, self._oam_indices, value, self._absolute_y, self.y)
        for x in range(self._width):
            for y in range(self._height):
                i = x * self._height + y
                v = value + 8 * y + 16
                if v < 0:
                    v = 0
                self._oam_entries[i][0] = v
                if self._oam_indices[0] is not None:
                    offset = self._compute_oam_address(i) + 0
                    self._gb[offset] = v

    def _compute_oam_address(self, i):
        return 0xfe00 + 4 * (self._oam_indices[i])

    def _show(self, free_indices):
        if len(free_indices) < self._width * self._height:
            raise RuntimeError("Not enough sprites available")

        self._free_indices = free_indices
        for i in range(self._width * self._height):
            self._oam_indices[i] = free_indices.pop()
            oam_address = self._compute_oam_address(i)

            if _gbio.is_color():
                attributes = self._oam_entries[i][3]
                new_palette = tile_to_colors[self._oam_entries[i][2]]
                pt = self._gb._sprite_palettes
                new_palette_index = pt.alloc(new_palette)
                self._oam_entries[i][3] = (attributes & 0xf8) | new_palette_index
            self._gb[oam_address:oam_address + 4] = self._oam_entries[i]

    def _hide(self):
        for i in range(self._width * self._height):
            oam_address = self._compute_oam_address(i)
            if _gbio.is_color():
                old_palette_index = self._oam_entries[i][3] & 0x7
                self._gb._sprite_palettes.free(old_palette_index)
            self._gb[oam_address:oam_address + 4] = b"\x00\x00\x00\x00"
            self._free_indices.add(self._oam_indices[i])
            self._oam_indices[i] = None

    @property
    def flip_x(self):
        return (self._oam_entries[0][3] & (1 << 5)) != 0

    @flip_x.setter
    def flip_x(self, value):
        for i in range(self._width * self._height):
            self._oam_entries[i][3] &= ~(1 << 5)
            if value:
                self._oam_entries[i][3] |= 1 << 5

            if self._oam_indices[i] is not None:
                offset = self._compute_oam_address(i) + 3
                self._gb[offset] = self._oam_entries[i][3]

    @property
    def flip_y(self):
        return (self._oam_entries[0][3] & (1 << 6)) != 0

    @flip_x.setter
    def flip_y(self, value):
        for i in range(self._width * self._height):
            self._oam_entries[i][3] &= ~(1 << 6)
            if value:
                self._oam_entries[i][3] |= 1 << 6
                
            if self._oam_indices[i] is not None:
                offset = self._compute_oam_address(i) + 3
                self._gb[offset] = self._oam_entries[i][3]

class Group(AbsolutePositioner):
    def __init__(self, max_size=None, **kwargs):
        self._children = []
        super().__init__(**kwargs)
        self._free_indices = None
        print("init group", kwargs)

    def __len__(self):
        return len(self._children)

    def __getitem__(self, i):
        return self._children[i]

    def _update_x(self):
        for o in self:
            o._absolute_x = self.__absolute_x + self._x

    def _update_y(self):
        for o in self:
            o._absolute_y = self.__absolute_y + self._y

    def append(self, o):
        o._absolute_x = self.__absolute_x + self._x
        o._absolute_y = self.__absolute_y + self._y
        print("append", self, o, o._absolute_x, o._absolute_y)
        # Show the object after we update its absolute position so it doesn't flicker.
        if self._free_indices is not None:
            o._show(self._free_indices)
        self._children.append(o)

    def remove(self, o):
        o._hide()
        self._children.remove(o)

    def _show(self, free_indices):
        self._free_indices = free_indices

        for o in self:
            o._show(free_indices)
            print(o)

    def _hide(self):
        for o in self:
            o._hide()

class Tiles:
    def __init__(self, gb):
        self._gb = gb
        self._tile_data = bytearray(256 * 16)
        self.auto_show = True
        self._start_byte = None
        self._end_byte = None

    def show(self):
        if self._start_byte is not None and self._end_byte is not None:
            self._gb[0x8000 + self._start_byte:0x8000 + self._end_byte] = memoryview(self._tile_data)[self._start_byte:self._end_byte]

        self._start_byte = None
        self._end_byte = None

    def __setitem__(self, index, value):
        if not 0 <= value < 4:
            raise ValueError("Tile values are two bits")
        x = index % 8
        row = index // 128
        y = row % 8
        tile = (row // 8) * 16 + (index % 128) // 8

        byte_address = tile * 16 + y * 2

        if self._start_byte is None or byte_address < self._start_byte:
            self._start_byte = byte_address
        if self._end_byte is None or (byte_address + 1) > self._end_byte:
            self._end_byte = byte_address + 1

        # if row < 16:
        #     print(index, byte_address, tile, x, y, value)

        mask = 1 << (7 - x)
        if value & 0x1 != 0:
            self._tile_data[byte_address] |= mask
        else:
            self._tile_data[byte_address] &= ~mask
        if value & 0x2 != 0:
            self._tile_data[byte_address + 1] |= mask
        else:
            self._tile_data[byte_address + 1] &= ~mask

    def __getitem__(self, index):
        x = index % 8
        row = index // 128
        y = row % 8
        tile = (row // 8) * 16 + (index % 128) // 8

        byte_address = tile * 16 + y * 2

        mask = 1 << x
        v = 0
        if (self._tile_data[byte_address] & mask) != 0:
            v += 1
        if (self._tile_data[byte_address + 1] & mask) != 0:
            v += 2
        return v

OAM_OFFSET = 0xfe00 - 0xc000

class GameBoy:
    def __init__(self):
        _gbio.reset_gameboy()

        self._byte_buf = bytearray(6)
        self._byte_buf[0] = 0x00 # Noop to sync DMA to GB clock
        self._byte_buf[1] = 0x0e # Load next value into C
        # Value into C
        self._byte_buf[3] = 0x3e # Load next value into A
        # Value into A
        self._byte_buf[5] = 0xe2 # Load A into 0xff00 + C


        self._full_address = bytearray(6)
        self._full_address[0] = 0x21 # Load next value into HL
        # Value into C
        self._full_address[3] = 0x3e # Load next value into A
        # Value into A
        self._full_address[5] = 0x22 # Load A into HL's address

        self._slice_buffer = bytearray(200)

        self.background = Background(self)
        self.tiles = Tiles(self)

        self._sprite_allocation = set()
        self._sprite_palettes = PaletteTracker(self, True)

        self._queued_oam_dma = False

        # DMA routine
        self[0xff80:0xff8b] = (b"\x3e\xc0" # Load 0xc0 into A
                               b"\xe0\x46" # Trigger dma by writing A to DMA
                               b"\x3e\x28" # Load delay length (0x28) into A
                               b"\x3d" # Decrement a
                               b"\xc2\x86\xff" # Jump back to decrement if not zero
                               b"\xc9") # Return

        # Clear the OAM
        for i in range(40):
            oam_address = 0xfe00 + 4 * i
            self[oam_address:oam_address + 4] = b"\x00\x00\x00\x00"

        self._color = _gbio.is_color()
        if self._color:
            # Set vram bank to 1
            self[0xff4f] = 0x1

            blank = b"\x00"*32
            for i in range(32):
                start = 0x9800 + 32 * i
                self[start:start+32] = blank
            # Set vram bank to 0
            self[0xff4f] = 0x0
        else:
            # Set the background palette
            self[0xff47] = 0b00011110

            # Set object palette 0
            self[0xff48] = 0b00011110

        self[0xff47] = 0b10001101

        _gbio.set_lcdc(0b10010011)


        self._group = None

    @property
    def lcd_display_enable(self):
        return _gbio.get_lcdc() & 0x80 != 0

    @lcd_display_enable.setter
    def lcd_display_enable(self, value):
        lcdc = _gbio.get_lcdc() & 0x7f
        _gbio.set_lcdc((0x80 if value else 0) | lcdc)

    def show(self, group):
        if group == self._group:
            return

        if self._group:
            self._group._hide()
        group._show(set(range(40)))
        self._group = group

    def wait_for_frame(self):
        _gbio.wait_for_vblank()
        self._queued_oam_dma = False

    def __setitem__(self, index, value):
        oam = False
        if isinstance(index, int):
            # if index == 0xff47 or index == 0xff48:
            #     raise RuntimeError()
            if index > 0xff00:
                self._byte_buf[2] = index - 0xff00
                self._byte_buf[4] = value
                # Special case the gameboy color palette registers and the vram bank switch.
                # Although the palette index register can be accessed outside vblank, we treat it
                # like it is to ensure access ordering.
                if 0xff68 <= index <= 0xff6b or index == 0xff4f:
                    _gbio.queue_vblank_commands(self._byte_buf, additional_cycles=1)
                else:
                    _gbio.queue_commands(self._byte_buf)
            else:
                if (index & 0xff00) == 0xfe00:
                    index -= OAM_OFFSET
                    oam = True
                self._full_address[1] = index & 0xff
                self._full_address[2] = (index >> 8) & 0xff
                self._full_address[4] = value
                if self.lcd_display_enable and (0x8000 <= index <= 0x9fff or 0xfe00 <= index <= 0xfe9f):
                    _gbio.queue_vblank_commands(self._full_address, additional_cycles=2)
                else:
                    _gbio.queue_commands(self._full_address)
        elif isinstance(index, slice):
            bc = 0
            out = None
            a = 256
            additional_cycles = 0
            vram = True
            start = index.start
            stop = index.stop
            if (start & 0xff00) == 0xfe00:
                start -= OAM_OFFSET
                stop -= OAM_OFFSET
                vram = False
                oam = True
            for i in range(stop - start):
                if out is None or out > len(self._slice_buffer) - 4:
                    if out:
                        if vram:
                            _gbio.queue_vblank_commands(memoryview(self._slice_buffer)[:out], additional_cycles=additional_cycles)
                        else:
                            _gbio.queue_commands(memoryview(self._slice_buffer)[:out])
                    out = 1 # position in command
                    addr = start + i
                    self._slice_buffer[out] = 0x21
                    self._slice_buffer[out + 1] = addr & 0xff
                    self._slice_buffer[out + 2] = (addr >> 8) & 0xff
                    out += 3
                    additional_cycles += 2
                # If data is different then load it into a
                if a != value[i]:
                    self._slice_buffer[out] = 0x3e # load immediate into A
                    self._slice_buffer[out + 1] = value[i] & 0xff
                    a = value[i]
                    out += 2
                self._slice_buffer[out] = 0x22 # load A into HL and increment HL
                additional_cycles += 1
                out += 1
            if out:
                if vram:
                    _gbio.queue_vblank_commands(memoryview(self._slice_buffer)[:out], additional_cycles=additional_cycles)
                else:
                    _gbio.queue_commands(memoryview(self._slice_buffer)[:out])
        if oam and not self._queued_oam_dma:
            _gbio.queue_vblank_commands(b"\xc3\x80\xff", additional_cycles=130)
            self._queued_oam_dma = True

gb = GameBoy()
