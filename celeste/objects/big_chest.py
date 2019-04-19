import pico8 as p8

from .celeste_object import CelesteObject
from .player import Player

class Particle:
    def __init__(self, x, y, h, spd):
        self.x = x
        self.y = y
        self.h = h
        self.spd = spd

class BigChest(CelesteObject):
    tile = 96
    def __init__(self):
        super().__init__()
        self.state=0
        self.hitbox.w=16

    def draw(self):
        if self.state == 0:
            hit = self.collide(Player,0,8)
            if hit and hit.is_solid(0,1):
                music(-1,500,7)
                sfx(37)
                pause_player=true
                hit.spd.x=0
                hit.spd.y=0
                self.state=1
                init_object(smoke,self.x,self.y)
                init_object(smoke,self.x+8,self.y)
                self.timer=60
                self.particles={}
            spr(96,self.x,self.y)
            spr(97,self.x+8,self.y)
        elif self.state == 1:
            self.timer-=1
            shake=5
            flash_bg=true
            if self.timer<=45 and count(self.particles)<50:
                self.particles.append(Particle(x=1+p8.rnd(14),
                                               y=0,
                                               h=32+p8.rnd(32),
                                               spd=8+p8.rnd(8)))
            if self.timer<0:
                self.state=2
                self.particles={}
                flash_bg=false
                new_bg=true
                init_object(orb,self.x+4,self.y+4)
                pause_player=false
            for p in self.particles:
                p.y+=p.spd
                line(self.x+p.x,self.y+8-p.y,self.x+p.x,min(self.y+8-p.y+p.h,self.y+8),7)
        spr(112,self.x,self.y+8)
        spr(113,self.x+8,self.y+8)
