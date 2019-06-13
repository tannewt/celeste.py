from celeste import game
from celeste import geom

from .celeste_object import CelesteObject
from .player import Player
from .smoke import Smoke

import pico8 as p8

import math

class Balloon(CelesteObject):
    tile=22
    def __init__(self, **kwargs):
        super().__init__(single_tile=False, **kwargs)
        self.offset=p8.rnd(1)
        self.start=self.y
        self.timer=0
        self.hitbox= geom.Rect(x=-1,y=-1,w=10,h=10)
        self.popped = False

        self.balloon = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, tile_width=8, tile_height=8)
        self.string = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, tile_width=8, tile_height=8, x=0, y=6)
        self.append(self.balloon)
        self.append(self.string)

    def update(self):
        if not self.popped:
            self.offset+=0.01
            self.y=int(self.start+p8.sin(self.offset)*2)
            hit = self.collide(Player,0,0)
            if hit and hit.djump<game.max_djump:
                game.psfx(6)
                game.objects.append(Smoke(x=self.x, y=self.y))
                hit.djump=game.max_djump
                self.popped = True
                self.timer=60
                self.balloon[0] = 0
                self.string[0] = 0
            else:
                self.balloon[0] = 22
                self.string[0] = 13+int((self.offset*8)%3)
        elif self.timer>0:
            self.timer-=1
        else:
            game.psfx(7)
            game.objects.append(Smoke(x=self.x, y=self.y))
            self.popped = False

    def draw(self):
        pass
