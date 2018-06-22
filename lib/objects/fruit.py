from celeste import game
from celeste import geom

from .celeste_object import CelesteObject
from .player import Player
from .lifeup import LifeUp

import pico8 as p8

class Fruit(CelesteObject):
    tile=26
    if_not_fruit=true
    def __init__(self, x, y):
        super().__init__(x, y)
        self.start=self.y
        self.off=0

    def update(self):
        hit=self.collide(Player,0,0)
        if hit:
            hit.djump=max_djump
            sfx_timer=20
            p8.sfx(13)
            game.got_fruit[1+game.level_index()] = true
            game.objects.append(LifeUp(self.x,self.y))
            game.objects.remove(self)
        self.off+=1
        self.y=self.start+sin(self.off/40)*2.5
