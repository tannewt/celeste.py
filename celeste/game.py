import pico8 as p8

import os

class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
room = Room(x=0, y=0)
if p8.platform_id == "adafruit":
    objects = []
else:
    objects = p8.gb
freeze=0
shake=0
will_restart=False
delay_restart=0
got_fruit=[]
has_dashed=False
sfx_timer=0
has_key=False
pause_player=False
flash_bg=False
music_timer=0
frames = 0
start_game = False
start_game_flash = False
new_bg = False
dead_particles = []
seconds = 0
minutes = 0
max_djump = 1

if p8.platform_id == "adafruit":
    if "Pybadge" in os.uname().machine:
        k_left=7
        k_right=4
        k_up=6
        k_down=5
        k_jump=0 # B
        k_dash=1 # A
elif p8.platform_id == "gb" or p8.platform_id == "gbc":
    k_left=1
    k_right=0
    k_up=2
    k_down=3
    k_jump=5
    k_dash=4


def level_index():
    return room.x%8+room.y*8

def is_title():
    return level_index()==31

def load_room(x,y):
    global objects, room
    has_dashed=False
    has_key=False

    # reset object list
    objects = []

    # current room
    room.x = x
    room.y = y

    # entities
    for tx in range(16):
        for ty in range(16):
            tile = p8.mget(room.x*16+tx,room.y*16+ty)
            if tile==11:
                objects.append(Platform(tx*8, ty*8, -1))
            elif tile==12:
                objects.append(Platform(tx*8, ty*8, 1))
            else:
                if tile in types:
                    objects.append(types[tile](tx*8,ty*8))

    if not is_title():
        objects.append(RoomTitle(0,0))

def restart_room():
    global will_restart, delay_restart
    will_restart=True
    delay_restart=15

def next_room():
    global will_restart, delay_restart, room
    will_restart = True
    delay_restart = 1 # Reset next frame

    if room.x==2 and room.y==1:
        music(30,500,7)
    elif room.x==3 and room.y==1:
        music(20,500,7)
    elif room.x==4 and room.y==2:
        music(30,500,7)
    elif room.x==5 and room.y==3:
        music(30,500,7)

    if room.x==7:
        room.x = 0
        room.y += 1
    else:
        room.x += 1

def psfx(num):
    if sfx_timer <= 0:
        p8.sfx(num)
