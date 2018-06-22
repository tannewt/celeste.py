from celeste import game
from celeste import geom
import pico8 as p8

def sign(v):
    if v>0:
        return 1
    elif v<0:
        return -1
    return 0

def draw_time(x,y):
    s=game.seconds
    m=game.minutes%60
    h=p8.flr(game.minutes/60)

    p8.rectfill(x,y,x+32,y+6,0)
    p8._print("{:02d}:{:02d}:{:02d}".format(h,m,s),x+1,y+1,7)

class Hair:
    def __init__(self, x=0, y=0, size=0):
        self.x = x
        self.y = y
        self.size = size

def create_hair(obj):
    obj.hair=[]
    for i in range(5):
        obj.hair.append(Hair(x=obj.x,y=obj.y,size=max(1,min(2,3-i))))

def set_hair_color(djump):
    color = 12
    if djump == 1:
        color = 8
    elif djump == 2:
        color = (7+flr((game.frames/3)%2)*4)
    p8.pal(8, color)

def unset_hair_color():
    p8.pal(8,8)

def draw_hair(obj, facing):
    last = geom.Vec(x=obj.x+4-facing*2,y=obj.y+(4 if p8.btn(game.k_down) else 3))
    for h in obj.hair:
        h.x+=(last.x-h.x)/1.5
        h.y+=(last.y+0.5-h.y)/1.5
        p8.circfill(h.x,h.y,h.size,8)
        last=h

def clamp(val,a,b):
    return max(a, min(b, val))

def appr(val,target,amount):
    if val > target:
        return max(val - amount, target)
    return min(val + amount, target)

def maybe():
    return p8.rnd(1)<0.5
