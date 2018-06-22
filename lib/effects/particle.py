import pico8 as p8

import math

class Particle:
    def __init__(self, x, y, s, spd, off, c):
        self.x = x
        self.y = y
        self.s = s
        self.spd = spd
        self.off = off
        self.c = c

        def draw(self):
            self.x += self.spd
            self.y += math.sin(self.off)
            self.off+= min(0.05,self.spd/32)
            p8.rectfill(self.x,self.y,self.x+self.s,self.y+self.s,self.c)
            if self.x>128+4:
                self.x=-4
                self.y=p8.rnd(128)
