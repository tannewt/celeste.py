from celeste import game
from .celeste_object import CelesteObject
import pico8 as p8

from celeste import helper

class Smoke(CelesteObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spr=29
        self.spd.y=-0.1
        self.spd.x=0.3+p8.rnd(0.2)
        self.x+=int(-1+p8.rnd(2))
        self.y+=int(-1+p8.rnd(2))
        self.flip_x=helper.maybe()
        self.flip_y=helper.maybe()
        self.solids=False

    def update(self):
        self.spr+=0.2
        if self.spr>=32:
            game.objects.remove(self)
