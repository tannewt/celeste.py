from celeste import game
from celeste import geom

from .celeste_object import CelesteObject

import pico8 as p8

class LifeUp(CelesteObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spd.y=-0.25
        self.duration=30
        self.x-=2
        self.y-=4
        self.flash=0
        self.solids=False
        if p8.platform_id == "adafruit":
            self._text = p8._print("1000",-2,0,7)
            self.append(self._text)

    def update(self):
        self.duration-=1
        if self.duration<= 0:
            game.objects.remove(self)

    def draw(self):
        # self.flash+=0.5
        # Normally flashes but we may not have the palette to do it on gameboy so skip.
        pass
