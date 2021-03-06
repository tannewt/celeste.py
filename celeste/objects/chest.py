from celeste import game

from .celeste_object import CelesteObject
from .player import Player
from .fruit import Fruit

import pico8 as p8

class Chest(CelesteObject):
    tile=20
    if_not_fruit=True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x-=4
        self.start=self.x
        self.timer=20

    def update(self):
        if game.has_key:
            self.timer-=1
            self.x=int(self.start-1+p8.rnd(3))
            if self.timer<=0:
                game.sfx_timer=20
                p8.sfx(16)
                game.objects.append(Fruit(x=self.x, y=self.y-4))
                game.objects.remove(self)
