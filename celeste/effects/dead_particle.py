from celeste import game

import pico8 as p8

class DeadParticle:
    def __init__(self, x, y, t, spd):
        self.x = x
        self.y = y
        self.t = t
        self.spd = spd

    def draw(self):
        self.x += self.spd.x
        self.y += self.spd.y
        self.t -=1
        if self.t <= 0:
            game.dead_particles.remove(self)
        p8.rectfill(self.x-self.t/5,self.y-self.t/5,self.x+self.t/5,self.y+self.t/5,14+self.t%2)
