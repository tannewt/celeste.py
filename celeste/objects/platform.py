
from . import celeste_object
from .player import Player

class Platform(celeste_object.CelesteObject):
    def __init__(self, x, y, dir):
        super().__init__(x, y)
        self.x-=4
        self.solids=False
        self.hitbox.w=16
        self.last=self.x
        self.dir = dir

    def update(self):
        self.spd.x=self.dir*0.65
        if self.x<-16:
            self.x=128
        elif self.x>128:
            self.x=-16
        if not self.check(Player,0,0):
            hit=self.collide(Player,0,-1)
            if hit:
                hit.move_x(self.x-self.last,1)
        self.last=self.x

    def draw(self):
        spr(11,self.x,self.y-1)
        spr(12,self.x+8,self.y-1)

# ugly monkey patch to allow CelesteObject to reference Platform
celeste_object.Platform = Platform
