import math

from celeste import game

from .celeste_object import CelesteObject
from .player import Player

import pico8 as p8

class Key(CelesteObject):
    tile=8
    if_not_fruit=True
    def update(self):
        was=p8.flr(self.spr)
        self.spr=9+(math.sin(game.frames / 30)+0.5)*1
        current=p8.flr(self.spr)
        if current==10 and current!=was:
            self.flip.x=not self.flip.x

        if self.check(Player,0,0):
            p8.sfx(23)
            game.sfx_timer=10
            game.objects.remove(self)
            game.has_key=True
