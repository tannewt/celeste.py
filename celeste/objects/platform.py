
from . import celeste_object
from .player import Player

import pico8 as p8

class Platform(celeste_object.CelesteObject):
    def __init__(self, *, direction, **kwargs):
        super().__init__(single_tile=False, **kwargs)
        self.x-=4
        self.solids=False
        self.hitbox.w=16
        self.last=self.x
        self.dir = direction

        tg = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, width=2, height=1, tile_width=8, tile_height=8, y=-1)
        tg[0] = 11
        tg[1] = 12
        self.append(tg)

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
        pass

# ugly monkey patch to allow CelesteObject to reference Platform
celeste_object.Platform = Platform
