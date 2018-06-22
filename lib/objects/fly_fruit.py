from celeste import game
from celeste import geom

from .celeste_object import CelesteObject
from .player import Player
from .lifeup import LifeUp

import pico8 as p8

import math

class FlyFruit(CelesteObject):
    tile=28
    if_not_fruit = True
    def __init__(self, x, y):
        super().__init__(x, y)
        self.start=self.y
        self.fly=false
        self.step=0.5
        self.solids=false
        self.sfx_delay=8

    def update(self):
        # fly away
        if self.fly:
            if self.sfx_delay>0:
                self.sfx_delay-=1
                if self.sfx_delay<=0:
                    game.sfx_timer=20
                    p8.sfx(14)

            self.spd.y=appr(self.spd.y,-3.5,0.25)
            if self.y<-16:
                game.objects.remove(self)
        # wait
        else:
            if game.has_dashed:
                self.fly=True
            self.step+=0.05
            self.spd.y=math.sin(self.step)*0.5

        # collect
        hit=self.collide(Player,0,0)
        if hit:
            hit.djump=game.max_djump
            game.sfx_timer=20
            p8.sfx(13)
            game.got_fruit[1+game.level_index()] = True
            game.objects.append(LifeUp(self.x,self.y))
            game.objects.remove(self)

    def draw(self):
        off=0
        if not self.fly:
            dir=math.sin(self.step)
            if dir<0:
                off=1+max(0,sign(self.y-self.start))
        else:
            off=(off+0.25)%3
        p8.spr(45+off,self.x-6,self.y-2,1,1,True,False)
        p8.spr(self.spr,self.x,self.y)
        p8.spr(45+off,self.x+6,self.y-2)
