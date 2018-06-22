from celeste import game

from .celeste_object import CelesteObject
from .player import Player

import pico8 as p8

import math

class Orb(CelesteObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.spd.y=-4
        self.solids=False
        self.particles=[]

    def draw(self):
        self.spd.y=appr(self.spd.y,0,0.5)
        hit=self.collide(Player,0,0)
        if self.spd.y==0 and hit:
            game.music_timer=45
            p8.sfx(51)
            game.freeze=10
            game.shake=10
            game.objects.remove(self)
            game.max_djump=2
            hit.djump=2

        p8.spr(102,self.x,self.y)
        off=game.frames/30
        for i in range(7):
            p8.circfill(self.x+4+math.cos(off+i/8)*8,self.y+4+math.sin(off+i/8)*8,1,7)
