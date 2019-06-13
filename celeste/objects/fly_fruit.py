from celeste import game
from celeste import geom
from celeste import helper

from .celeste_object import CelesteObject
from .player import Player
from .lifeup import LifeUp

import pico8 as p8

class FlyFruit(CelesteObject):
    tile=28
    if_not_fruit = True
    def __init__(self, **kwargs):
        super().__init__(single_tile=False, **kwargs)
        self.start=self.y
        self.fly=False
        self.step=0.5
        self.solids=False
        self.sfx_delay=8
        self.left = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, tile_width=8, tile_height=8, x=-6, y=-2)
        self.left.flip_x = True
        self.main = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, tile_width=8, tile_height=8)
        self.right = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, tile_width=8, tile_height=8, x=6, y=-2)
        self.append(self.left)
        self.append(self.main)
        self.append(self.right)

    def update(self):
        # fly away
        if self.fly:
            if self.sfx_delay>0:
                self.sfx_delay-=1
                if self.sfx_delay<=0:
                    game.sfx_timer=20
                    p8.sfx(14)

            self.spd.y=helper.appr(self.spd.y,-3.5,0.25)
            if self.y<-16:
                game.objects.remove(self)
        # wait
        else:
            if game.has_dashed:
                self.fly=True
            self.step+=0.05
            self.spd.y=p8.sin(self.step)*0.5

        # collect
        hit=self.collide(Player,0,0)
        if hit:
            hit.djump=game.max_djump
            game.sfx_timer=20
            p8.sfx(13)
            game.got_fruit[1+game.level_index()] = True
            game.objects.append(LifeUp(x=self.x, y=self.y))
            game.objects.remove(self)

    def draw(self):
        off=0
        if not self.fly:
            dir=p8.sin(self.step)
            if dir<0:
                off=int(1+max(0,helper.sign(self.y-self.start)))
        else:
            off=int((off+0.25)%3)
        self.left[0] = 45+off
        self.main[0] = 28
        self.right[0] = 45+off
