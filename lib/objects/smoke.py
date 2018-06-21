from celeste import game
from .celeste_object import CelesteObject
import pico8 as p8

class Smoke(CelesteObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.spr=29
        self.spd.y=-0.1
        self.spd.x=0.3+p8.rnd(0.2)
        self.x+=-1+p8.rnd(2)
        self.y+=-1+p8.rnd(2)
        self.flip.x=p8.maybe()
        self.flip.y=p8.maybe()
        self.solids=False

    def update(self):
        self.spr+=0.2
        if self.spr>=32:
            game.objects.remove(self)
