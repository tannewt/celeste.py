from celeste import game

from .celeste_object import CelesteObject
from .player import Player
from .smoke import Smoke

class Spring(CelesteObject):
    tile=18
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hide_in=0
        self.hide_for=0

    def _break(self):
        self.hide_in = 15

    def update(self):
        if self.hide_for>0:
            self.hide_for-=1
            if self.hide_for<=0:
                self.spr=18
                self.delay=0
        elif self.spr==18:
            hit = self.collide(Player,0,0)
            if hit and hit.spd.y>=0:
                self.spr=19
                hit.y=self.y-4
                hit.spd.x*=0.2
                hit.spd.y=-3
                hit.djump=game.max_djump
                self.delay=10
                game.objects.append(Smoke(x=self.x, y=self.y))

                # breakable below us
                below=self.collide(FallFloor,0,1)
                if below:
                    below._break()

                game.psfx(8)
        elif self.delay>0:
            self.delay-=1
            if self.delay<=0:
                self.spr=18

        # begin hiding
        if self.hide_in>0:
            self.hide_in-=1
            if self.hide_in<=0:
                self.hide_for=60
                self.spr=0
