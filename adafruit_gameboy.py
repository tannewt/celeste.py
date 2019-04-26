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

class Tiles:
    def __init__(self, gb):
        self._gb = gb
        self._tile_data = bytearray(256 * 16)
        self.auto_show = True
        self._start_byte = None
        self._end_byte = None

    def show(self):
        print("update", self._start_byte, self._end_byte)
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

        # Set the palette
        self[0xff47] = 0b00011011

    @property
    def lcd_display_enable(self):
        return gbio.get_lcdc() & 0x80 != 0

    @lcd_display_enable.setter
    def lcd_display_enable(self, value):
        lcdc = gbio.get_lcdc() & 0x7f
        gbio.set_lcdc((0x80 if value else 0) | lcdc)

    def __setitem__(self, index, value):
        if isinstance(index, int):
            if index > 0xff00:
                self._byte_buf[2] = index - 0xff00
                self._byte_buf[4] = value
                gbio.queue_commands(self._byte_buf)
            else:
                self._full_address[1] = index & 0xff
                self._full_address[2] = (index >> 8) & 0xff
                self._full_address[4] = value
                if self.lcd_display_enable and (0x8000 <= index <= 0x9fff or 0xfe00 <= index <= 0xfe9f):
                    print("vblank", hex(index), value)
                    gbio.queue_vblank_commands(self._full_address, additional_cycles=2)
                else:
                    gbio.queue_commands(self._full_address)
        elif isinstance(index, slice):
            print("unsupported slice", index, value)
            bc = 0
            out = None
            a = 256
            additional_cycles = 0
            for i in range(index.stop - index.start):
                if out is None or out > len(self._slice_buffer) - 4:
                    if out:
                        gbio.queue_vblank_commands(memoryview(self._slice_buffer)[:out], additional_cycles=additional_cycles)
                    out = 1 # position in command
                    addr = i + index.start
                    print(hex(addr))
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
                gbio.queue_vblank_commands(memoryview(self._slice_buffer)[:out], additional_cycles=additional_cycles)

gb = GameBoy()
