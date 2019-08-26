from celeste import game

from . import celeste_object
from .player import Player
from .smoke import Smoke
from . import spring

import pico8 as p8

class FallFloor(celeste_object.CelesteObject):
    tile=23
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state=0
        self.solid=True

    def _break(self):
        if self.state==0:
            game.psfx(15)
            self.state=1
            self.delay=15 # how long until it falls
            game.objects.append(Smoke(x=self.x, y=self.y))
            s=self.collide(spring.Spring,0,-1)
            if s:
                s._break()

    def update(self):
        # idling
        if self.state == 0:
            if (self.collide_with_player(0,-1) or
                self.collide_with_player(-1,0) or
                self.collide_with_player(1,0)):
                self._break()

        # shaking
        elif self.state==1:
            self.delay-=1
            print("shake", self.delay)
            if self.delay<=0:
                self.state=2
                self.delay=60 #how long it hides for
                self.collideable=False

        # invisible, waiting to reset
        elif self.state==2:
            self.delay-=1
            if self.delay<=0 and not self.collide_with_player(0,0):
                game.psfx(7)
                self.state=0
                self.collideable=True
                game.objects.append(Smoke(x=self.x, y=self.y))

    def draw(self):
        if self.state!=2:
            if self.state!=1:
                self.spr = 23
            else:
                self.spr = 23 + (15 - self.delay) // 5
        else:
            self.spr = 0


# ugly monkey patch to allow CelesteObject to reference FallFloor
celeste_object.FallFloor = FallFloor
spring.FallFloor = FallFloor
