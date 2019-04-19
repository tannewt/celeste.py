from celeste import game

from .celeste_object import CelesteObject
from .player import Player

import pico8 as p8

class Flag(CelesteObject):
    tile=118
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x+=5
        self.score=0
        self.show=False
        for fruit in game.got_fruit:
            if fruit:
                self.score+=1

    def draw(self):
        self.spr=118+(frames/5)%3
        p8.spr(self.spr,self.x,self.y)
        if self.show:
            p8.rectfill(32,2,96,31,0)
            p8.spr(26,55,6)
            p8._print("x{}".format(self.score),64,9,7)
            draw_time(49,16)
            p8._print("deaths:{}".format(deaths),48,24,7)
        elif self.check(Player,0,0):
            p8.sfx(55)
            game.sfx_timer=30
            self.show=True
