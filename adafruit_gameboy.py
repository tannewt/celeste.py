import gbio

class Background:
    def __init__(self, gb):
        self._gb = gb
        self._x = 0
        self._y = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._gb[0xff43] = 255 - value

    @property
    def y(self):
        return self._y

    @x.setter
    def y(self, value):
        self._y = value
        self._gb[0xff42] = 255 - value

    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            index = index[0] * 32 + index[1]
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
    def __init__(self, bitmap, *, pixel_shader, width=1, height=1, **kwargs):
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
        print("set sprite", self._oam_indices, index, value)
        self._oam_entries[index][2] = value
        if self._oam_indices[index] is not None:
            offset = self._compute_oam_address(index) + 2
            self._gb[offset] = value

    def _update_x(self):
        value = int(self._absolute_x + self.x)
        print("set sprite x", self, self._oam_indices, value)
        if self._last_value is not None and self._free_indices is not None and value - self._last_value == 16:
            raise RuntimeError()
        self._last_value = value
        for x in range(self._width):
            for y in range(self._height):
                i = x * self._width + y
                v = value + 8 * x + 8
                self._oam_entries[i][1] = v
                if self._oam_indices[i] is not None:
                    offset = self._compute_oam_address(i) + 1
                    self._gb[offset] = v

    def _update_y(self):
        value = int(self._absolute_y + self.y)
        print("set sprite y", self, self._oam_indices, value)
        for x in range(self._width):
            for y in range(self._height):
                i = x * self._width + y
                v = value + 8 * y + 16
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
        print("show tilegrid", self, self._oam_indices)
        for i in range(self._width * self._height):
            self._oam_indices[i] = free_indices.pop()
            oam_address = self._compute_oam_address(i)
            print(self._oam_entries[i])
            self._gb[oam_address:oam_address + 4] = self._oam_entries[i]

    def _hide(self):
        for i in range(self._width * self._height):
            oam_address = self._compute_oam_address(i)
            self._gb[oam_address:oam_address + 4] = b"\x00\x00\x00\x00"
            self._free_indices.add(self._oam_indices[i])
            self._oam_indices[i] = None

class Group(AbsolutePositioner):
    def __init__(self, **kwargs):
        self._children = []
        super().__init__(**kwargs)
        self._free_indices = None
        print("init group")

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



        self._color = gbio.is_color()
        if self._color:
            # Set vram bank to 0
            self[0xff4f] = 0x0

            # Set the background palette
            self[0xff68] = 0x80

            # Index 0
            self[0xff69] = 0x1f
            self[0xff69] = 0xf1

            # Index 1
            self[0xff69] = 0x1f
            self[0xff69] = 0xf1

            # Index 2
            self[0xff69] = 0x1f
            self[0xff69] = 0xf1

            # Index 3
            self[0xff69] = 0x1f
            self[0xff69] = 0xf1
        else:
            # Set the background palette
            self[0xff47] = 0b00011110

            # Set object palette 0
            self[0xff48] = 0b00011110


        gbio.set_lcdc(0b10010011)


        self._group = None

    @property
    def lcd_display_enable(self):
        return gbio.get_lcdc() & 0x80 != 0

    @lcd_display_enable.setter
    def lcd_display_enable(self, value):
        lcdc = gbio.get_lcdc() & 0x7f
        gbio.set_lcdc((0x80 if value else 0) | lcdc)

    def show(self, group):
        if group == self._group:
            return

        if self._group:
            self._group._hide()
        group._show(set(range(40)))
        self._group = group

    def wait_for_frame(self):
        gbio.wait_for_vblank()
        self._queued_oam_dma = False

    def __setitem__(self, index, value):
        oam = False
        if isinstance(index, int):
            if index > 0xff00:
                self._byte_buf[2] = index - 0xff00
                self._byte_buf[4] = value
                gbio.queue_commands(self._byte_buf)
            else:
                if (index & 0xff00) == 0xfe00:
                    index -= OAM_OFFSET
                    oam = True
                self._full_address[1] = index & 0xff
                self._full_address[2] = (index >> 8) & 0xff
                self._full_address[4] = value
                if self.lcd_display_enable and (0x8000 <= index <= 0x9fff or 0xfe00 <= index <= 0xfe9f):
                    gbio.queue_vblank_commands(self._full_address, additional_cycles=2)
                else:
                    gbio.queue_commands(self._full_address)
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
                            gbio.queue_vblank_commands(memoryview(self._slice_buffer)[:out], additional_cycles=additional_cycles)
                        else:
                            gbio.queue_commands(memoryview(self._slice_buffer)[:out])
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
                    gbio.queue_vblank_commands(memoryview(self._slice_buffer)[:out], additional_cycles=additional_cycles)
                else:
                    gbio.queue_commands(memoryview(self._slice_buffer)[:out])
        if oam and not self._queued_oam_dma:
            gbio.queue_vblank_commands(b"\xc3\x80\xff", additional_cycles=130)
            self._queued_oam_dma = True

gb = GameBoy()
