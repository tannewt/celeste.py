import struct
import time


class ILI9341:
    """A minimal driver for the 128x128 version of the ST7735 SPI display."""

    width = 320
    height = 240

    def __init__(self, spi, dc, cs, rotation=0x06):
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.dc.switch_to_output(value=1)
        self.rotation = rotation
        time.sleep(0.1)
        mapping = bytearray(128)
        for i in range(32):
            mapping[i] = i * 2
            mapping[96 + i] = i * 2

        for i in range(64):
            mapping[32 + i] = i

        for command, data in (
            (b'\xef', b'\x03\x80\x02'),
            (b'\xcf', b'\x00\xc1\x30'),
            (b'\xed', b'\x64\x03\x12\x81'),
            (b'\xe8', b'\x85\x00\x78'),
            (b'\xcb', b'\x39\x2c\x00\x34\x02'),
            (b'\xf7', b'\x20'),
            (b'\xea', b'\x00\x00'),
            (b'\xc0', b'\x23'),  # Power Control 1, VRH[5:0]
            (b'\xc1', b'\x10'),  # Power Control 2, SAP[2:0], BT[3:0]
            (b'\xc5', b'\x3e\x28'),  # VCM Control 1
            (b'\xc7', b'\x86'),  # VCM Control 2
            (b'\x36', b'\x34'),  # Memory Access Control
            (b'\x3a', b'\x55'),  # Pixel Format
            (b'\xb1', b'\x00\x18'),  # FRMCTR1
            (b'\xb6', b'\x08\x82\x27'),  # Display Function Control
            (b'\xf2', b'\x00'),  # 3Gamma Function Disable
            (b'\x26', b'\x01'),  # Gamma Curve Selected
            (b'\xe0',  # Set Gamma
             b'\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00'),
            (b'\xe1',  # Set Gamma
             b'\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f'),
            (b'\x11', None),
            (b'\x2d', bytes(mapping)),
            (b'\x29', None),
            (b'\x38', None),
        ):
            self.write(command, data)
        self.dc.value = 0

    def block(self, x0, y0, x1, y1):
        """Prepare for updating a block of the screen."""
        # if self.rotation & 0x01:
        #     x0 += 3
        #     x1 += 3
        #     y0 += 2
        #     y1 += 2
        # else:
        #     x0 += 2
        #     x1 += 2
        #     y0 += 3
        #     y1 += 3
        xpos = struct.pack('>HH', x0*2, x1*2-1)
        #print("x", x0*2, x1*2-1, "y", y0*2, y1*2-1)
        ypos = struct.pack('>HH', y0*2, y1*2-1)
        self.write(b'\x2a', xpos)
        self.write(b'\x2b', ypos)
        self.write(b'\x2c')
        self.dc.value = True

    def write(self, command=None, data=None):
        """Send command and/or data to the display."""

        while not self.spi.try_lock():
            pass
        self.spi.configure(baudrate=24000000, polarity=0, phase=0)
        self.cs.value = False
        if command is not None:
            self.dc.value = 0
            self.spi.write(command)
        if data:
            self.dc.value = 1
            self.spi.write(data)
        self.cs.value = True
        self.spi.unlock()

    def clear(self, color=0x00):
        """Clear the display with the given color."""

        self.block(0, 0, self.width - 1, self.height - 1)
        pixel = color.to_bytes(2, 'big')
        data = pixel * 256
        for count in range(self.width * self.height // 256):
            self.write(None, data)
