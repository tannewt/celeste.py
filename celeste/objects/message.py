from celeste import game
from celeste import geom

from .celeste_object import CelesteObject
from .player import Player
from .smoke import Smoke

import pico8 as p8

import math

class Message(CelesteObject):
    tile=86
    def __init__(self, x, y):
        super().__init__(x, y)
        self.last = 0

    def draw(self):
        self.text="-- celeste mountain --#self memorial to those# perished on the climb"
        if self.check(Player,4,0):
            if self.index<len(self.text):
                self.index+=0.5
                if self.index>=self.last+1:
                    self.last+=1
                    p8.sfx(35)

            self.off=geom.Vec(x=8,y=96)
            for i in range(self.index):
                if self.text[i] != "#":
                    p8.rectfill(self.off.x-2,self.off.y-2,self.off.x+7,self.off.y+6 ,7)
                    p8._print(self.text[i],self.off.x,self.off.y,0)
                    self.off.x+=5
                else:
                    self.off.x=8
                    self.off.y+=7
        else:
            self.index=0
            self.last=0
