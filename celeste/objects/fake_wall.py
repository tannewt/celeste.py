from celeste import game
from celeste import geom

from . import celeste_object
from .player import Player
from .smoke import Smoke
from .fruit import Fruit

import pico8 as p8

from celeste import helper

class FakeWall(celeste_object.CelesteObject):
    tile=64
    if_not_fruit=True

    def __init__(self, **kwargs):
        super().__init__(single_tile=False, **kwargs)
        tg = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, width=2, height=2, tile_width=8, tile_height=8)
        tg[0] = 64
        tg[1] = 65
        tg[2] = 80
        tg[3] = 81
        self.append(tg)

    def update(self):
        self.hitbox = geom.Rect(x=-1,y=-1,w=18,h=18)
        hit = self.collide_with_player(0,0)
        if hit and hit.dash_effect_time>0:
            hit.spd.x=-helper.sign(hit.spd.x)*1.5
            hit.spd.y=-1.5
            hit.dash_time=-1
            game.sfx_timer=20
            p8.sfx(16)
            game.objects.remove(self)
            game.objects.append(Smoke(x=self.x, y=self.y))
            game.objects.append(Smoke(x=self.x+8, y=self.y))
            game.objects.append(Smoke(x=self.x, y=self.y+8))
            game.objects.append(Smoke(x=self.x+8, y=self.y+8))
            game.objects.append(Fruit(x=self.x+4, y=self.y+4))
        self.hitbox = geom.Rect(x=0,y=0,w=16,h=16)

    def draw(self):
        pass

# ugly monkey patch to allow CelesteObject to reference FakeWall
celeste_object.FakeWall = FakeWall
