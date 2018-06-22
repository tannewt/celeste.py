from celeste import game
from celeste import geom

from .celeste_object import CelesteObject
from .player import Player
from .smoke import Smoke
from .fruit import Fruit

import pico8 as p8

class FakeWall(CelesteObject):
    tile=64
    if_not_fruit=True

    def update(self):
        self.hitbox = geom.Rect(x=-1,y=-1,w=18,h=18)
        hit = self.collide(Player,0,0)
        if hit and hit.dash_effect_time>0:
            hit.spd.x=-sign(hit.spd.x)*1.5
            hit.spd.y=-1.5
            hit.dash_time=-1
            sfx_timer=20
            sfx(16)
            game.objects.remove(self)
            game.objects.append(Smoke(self.x,self.y))
            game.objects.append(Smoke(self.x+8,self.y))
            game.objects.append(Smoke(self.x,self.y+8))
            game.objects.append(Smoke(self.x+8,self.y+8))
            game.objects.append(Fruit(self.x+4,self.y+4))
        self.hitbox = geom.Rect(x=0,y=0,w=16,h=16)

    def draw(self):
        p8.spr(64,self.x,self.y)
        p8.spr(65,self.x+8,self.y)
        p8.spr(80,self.x,self.y+8)
        p8.spr(81,self.x+8,self.y+8)
