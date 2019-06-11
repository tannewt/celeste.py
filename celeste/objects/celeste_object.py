import math
import time

from .. import helper
from .. import geom

from celeste import game

import pico8 as p8

class Flip:
    def __init__(self):
        self.x = False
        self.y = False

class CelesteObject(p8.platform.Group):
    tile = 0
    def __init__(self, single_tile=True, **kwargs):
        super().__init__(**kwargs)
        self.collideable=True
        self.solids=True

        self._single_tile = single_tile
        self._sprite = None
        if single_tile and self.tile > 0:
            self.spr = self.tile

        self.flip = Flip()

        self.hitbox = geom.Rect(x=0, y=0, w=8, h=8)

        self.spd = geom.Vec()
        self.rem = geom.Vec()
        self._x = 0
        self._y = 0

    def collide(self, type, ox, oy):
        for other in game.objects:
            if (other and isinstance(other, type) and other != self and other.collideable and
                other.x+other.hitbox.x+other.hitbox.w > self.x+self.hitbox.x+ox and
                other.y+other.hitbox.y+other.hitbox.h > self.y+self.hitbox.y+oy and
                other.x+other.hitbox.x < self.x+self.hitbox.x+self.hitbox.w+ox and
                other.y+other.hitbox.y < self.y+self.hitbox.y+self.hitbox.h+oy):
                return other
        return None

    def _solid_at(self, ox, oy):
        return self._tile_flag_at(ox, oy, 0)

    def _ice_at(self, ox, oy):
        return self._tile_flag_at(ox, oy, 4)

    def _tile_flag_at(self, ox, oy, flag):
        x = self.x + self.hitbox.x + ox
        y = self.y + self.hitbox.y + oy
        w = self.hitbox.w
        h = self.hitbox.h
        for i in range(max(0 , x // 8), min(16,(x+w-1) // 8+1)):
            for j in range(max(0 , y // 8), min(16,(y+h-1) // 8 + 1)):
                tile = p8.mget(game.room.x * 16 + i, game.room.y * 16 + j)
                if p8.fget(tile, flag):
                    return True
        return False

    def _is_solid(self, ox, oy):
        if oy>0 and not self.check(Platform,ox,0) and self.check(Platform,ox,oy):
            return True
        return (self._solid_at(ox, oy)
                or self.check(FallFloor,ox,oy)
                or self.check(FakeWall,ox,oy))

    def _is_ice(self, ox, oy):
        return self._ice_at(ox, oy)

    def move(self, ox, oy):
        if ox == 0 and oy == 0:
            return
        #print("move", time.monotonic())
        # [x] get move amount
        self.rem.x += ox
        amount = math.floor(self.rem.x + 0.5)
        self.rem.x -= amount
        self.move_x(amount,0)

        # [y] get move amount
        self.rem.y += oy
        amount = math.floor(self.rem.y + 0.5)
        self.rem.y -= amount
        self.move_y(amount)
        #print("move", time.monotonic())

    def move_x(self, amount, start):
        if self.solids:
            step = helper.sign(amount)
            for i in range(start, abs(amount)+1):
                if self._is_solid(step * (i - start + 1), 0):
                    if i > start:
                        self.x += step * (i - start)
                    self.spd.x = 0
                    self.rem.x = 0
                    return
            self.x += step * (abs(amount) + 1)
        else:
            self.x += amount

    def move_y(self, amount):
        if self.solids:
            step = helper.sign(amount)
            for i in range(0, abs(amount)+1):
                if self._is_solid(0, step * (i + 1)):
                    if i > 0:
                        self.y += step * i
                    self.spd.y = 0
                    self.rem.y = 0
                    return
            self.y += step * (abs(amount) + 1)
        else:
            self.y += amount

    @property
    def spr(self):
        return self._spr

    @spr.setter
    def spr(self, s):
        # s can be a float if used in an animation
        self._spr = s
        if self._sprite is None and s > 0 and self._single_tile:
            self._sprite = p8.platform.TileGrid(p8.sprite_sheet, pixel_shader=p8.palette, tile_width=8, tile_height=8)
            self.append(self._sprite)
        self._sprite[0] = int(s)

    def check(self, type, ox, oy):
        return self.collide(type,ox,oy) is not None

    def update(self):
        pass

    def draw(self):
        pass

    # # We mask x because we need it to be a float.
    # @property
    # def x(self):
    #     return self._x
    #
    # @x.setter
    # def x(self, value):
    #     print("set x", value)
    #     self._x = value
    #     #super(p8.platform.Group, self).x = int(value)
    #     p8.platform.Group.x.fset()(self, int(value))
    #
    #
    # # We mask y because we need it to be a float.
    # @property
    # def y(self):
    #     print("get y", self._y)
    #     return self._y
    #
    # @x.setter
    # def y(self, value):
    #     print("set y", value)
    #     if value == 0:
    #         print(self.spd)
    #         # raise RuntimeError()
    #     self._y = value
    #     p8.platform.Group.y.fset()(self, int(value))
