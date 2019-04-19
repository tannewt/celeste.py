"""
A helper module that initializes the display and buttons for the uGame
game console. See https://hackaday.io/project/27629-game
"""

import board
import digitalio
import busio
import audioio
import analogio
import pulseio

import ili9341
import gamepad


K_X = 0x01
K_DOWN = 0x02
K_LEFT = 0x04
K_RIGHT = 0x08
K_UP = 0x10
K_O = 0x20


class Audio:
    last_audio = None

    def __init__(self):
        #self.mute_pin = digitalio.DigitalInOut(board.MUTE)
        #self.mute_pin.switch_to_output(value=1)
        pass

    def play(self, audio_file):
        self.stop()
        self.last_audio = audioio.AudioOut(board.A0, audio_file)
        self.last_audio.play()

    def stop(self):
        if self.last_audio:
            self.last_audio.stop()

    def mute(self, value=True):
        self.mute_pin.value = not value


dc = digitalio.DigitalInOut(board.D10)
cs = digitalio.DigitalInOut(board.D9)
cs.switch_to_output(value=True)
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

display = ili9341.ILI9341(spi, dc, cs, 0)

backlight = pulseio.PWMOut(board.D11)
backlight.duty_cycle = 2 ** 14

# buttons = gamepad.GamePad(
#     digitalio.DigitalInOut(board.X),
#     digitalio.DigitalInOut(board.DOWN),
#     digitalio.DigitalInOut(board.LEFT),
#     digitalio.DigitalInOut(board.RIGHT),
#     digitalio.DigitalInOut(board.UP),
#     digitalio.DigitalInOut(board.O),
# )

buttons = gamepad.GamePad(digitalio.DigitalInOut(board.D8), spi)

audio = Audio()

#battery = analogio.AnalogIn(board.BATTERY)
