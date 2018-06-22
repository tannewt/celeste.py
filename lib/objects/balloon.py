from celeste import game
from celeste import geom

from .celeste_object import CelesteObject
from .player import Player
from .smoke import Smoke

import pico8 as p8

import math

class Balloon(CelesteObject):
    tile=22
    def __init__(self, x, y):
        super().__init__(x, y)
        self.offset=p8.rnd(1)
        self.start=self.y
        self.timer=0
        self.hitbox= geom.Rect(x=-1,y=-1,w=10,h=10)

    def update(self):
        if self.spr==22:
            self.offset+=0.01
            self.y=self.start+math.sin(self.offset)*2
            hit = self.collide(Player,0,0)
            if hit and hit.djump<game.max_djump:
                game.psfx(6)
                game.objects.append(Smoke(self.x,self.y))
                hit.djump=game.max_djump
                self.spr=0
                self.timer=60
        elif self.timer>0:
            self.timer-=1
        else:
            game.psfx(7)
            game.objects.append(Smoke(self.x,self.y))
            self.spr=22

    def draw(self):
        if self.spr==22:
            p8.spr(13+(self.offset*8)%3,self.x,self.y+6)
            p8.spr(self.spr,self.x,self.y)
