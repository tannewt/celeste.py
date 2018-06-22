import pico8 as p8
from .celeste_object import CelesteObject
from celeste import game
from celeste import helper

class RoomTitle(CelesteObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.delay=5

    def draw(self):
        self.delay-=1
        if self.delay<-30:
            game.objects.remove(self)
        elif self.delay<0:
            p8.rectfill(24,58,104,70,0)
            # rect(26,64-10,102,64+10,7)
            # print("---",31,64-2,13)
            if game.room.x==3 and game.room.y==1:
                p8._print("old site",48,62,7)
            elif game.level_index()==30:
                p8._print("summit",52,62,7)
            else:
                level=(1+game.level_index())*100
                p8._print(str(level) + " m",52+(level<1000 and 2 or 0),62,7)

            # p8._print("---",86,64-2,13)

            helper.draw_time(4,4)
