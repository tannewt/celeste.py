import math
from .. import helper
from .. import geom

from celeste import game

import pico8 as p8

class Flip:
    def __init__(self):
        self.x = False
        self.y = False

class CelesteObject:
    def __init__(self, x=0, y=0):
        self.collideable=True
        self.solids=True

        self.flip = Flip()

        self.x = x
        self.y = y
        self.hitbox = geom.Rect(x=0, y=0, w=8, h=8)

        self.spd = geom.Vec()
        self.rem = geom.Vec()

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
        x = self.x+self.hitbox.x + ox
        y = self.y+self.hitbox.y + oy
        w = self.hitbox.w
        h = self.hitbox.h
        for i in range(max(0 , x // 8), min(15,(x+w-1) // 8+1)):
            for j in range(max(0 , y // 8), min(15,(y+h-1) // 8 + 1)):
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

    def move_x(self, amount, start):
        if self.solids:
            step = helper.sign(amount)
            for i in range(start, abs(amount)+1):
                if not self._is_solid(step, 0):
                    self.x += step
                else:
                    self.spd.x = 0
                    self.rem.x = 0
                    break
        else:
            self.x += amount

    def move_y(self, amount):
        if self.solids:
            step = helper.sign(amount)
            for i in range(0, abs(amount)+1):
                if not self._is_solid(0,step):
                    self.y += step
                else:
                    self.spd.y = 0
                    self.rem.y = 0
                    break
        else:
            self.y += amount


    def check(self, type, ox, oy):
        return self.collide(type,ox,oy) is not None

    def update(self):
        pass

    def draw(self):
        if self.spr > 0:
            p8.spr(self.spr,self.x,self.y,1,1,self.flip.x,self.flip.y)
