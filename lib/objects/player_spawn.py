from celeste import game
from celeste import geom

from .player import Player
from .smoke import Smoke
from .celeste_object import CelesteObject
from celeste import helper

import pico8 as p8

class PlayerSpawn(CelesteObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        p8.sfx(4)
        self.spr=3
        self.target= geom.Vec(x=self.x,y=self.y)
        self.y=128
        self.spd.y=-4
        self.state=0
        self.delay=0
        self.solids=False
        helper.create_hair(self)

    def update(self):
        # jumping up
        if self.state==0:
            if self.y < self.target.y+16:
                self.state=1
                self.delay=3
        # falling
        elif self.state==1:
            self.spd.y+=0.5
            if self.spd.y>0 and self.delay>0:
                self.spd.y=0
                self.delay-=1
            if self.spd.y>0 and self.y > self.target.y:
                self.y=self.target.y
                self.spd = geom.Vec(x=0,y=0)
                self.state=2
                self.delay=5
                shake=5
                game.objects.append(Smoke(self.x,self.y+4))
                sfx(5)
        # landing
        elif self.state==2:
            self.delay-=1
            self.spr=6
            if self.delay<0:
                game.objects.remove(self)
                game.objects.append(Player(self.x,self.y))

    def draw(self):
        helper.set_hair_color(game.max_djump)
        helper.draw_hair(self,1)
        p8.spr(self.spr,self.x,self.y,1,1,self.flip.x,self.flip.y)
        helper.unset_hair_color()
