from celeste import game

import pico8 as p8

class Cloud:
    def __init__(self, x, y, spd, w):
        self.x = x
        self.y = y
        self.spd = spd
        self.w = w

    def draw(self):
        self.x += self.spd
        p8.rectfill(self.x,self.y,self.x+self.w,self.y+4+(1-self.w/64)*12,14 if game.new_bg else 1)
        if self.x > 128:
            self.x = -self.w
            self.y=p8.rnd(128-8)
