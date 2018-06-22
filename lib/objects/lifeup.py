from celeste import game
from celeste import geom

from .celeste_object import CelesteObject

import pico8 as p8

class LifeUp(CelesteObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.spd.y=-0.25
        self.duration=30
        self.x-=2
        self.y-=4
        self.flash=0
        self.solids=False

    def update(self):
        self.duration-=1
        if self.duration<= 0:
            game.objects.remove(self)

    def draw(self):
        self.flash+=0.5

        p8._print("1000",self.x-2,self.y,7+self.flash%2)
