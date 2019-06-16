# ~celeste~
# matt thorson + noel berry
# ported to python by scott shawcroft (@tannewt)
import board
import time
last_checkpoint = time.monotonic()

# import busio
# import displayio
# from microcontroller import pin
# import board

import pico8 as p8

from celeste.effects.cloud import Cloud
from celeste.effects.particle import Particle
from celeste.objects.balloon import Balloon
from celeste.objects.big_chest import BigChest
from celeste.objects.chest import Chest
from celeste.objects.fake_wall import FakeWall
from celeste.objects.fall_floor import FallFloor
from celeste.objects.flag import Flag
from celeste.objects.fly_fruit import FlyFruit
from celeste.objects.fruit import Fruit
from celeste.objects.key import Key
from celeste.objects.message import Message
from celeste.objects.platform import Platform
from celeste.objects.player_spawn import PlayerSpawn
from celeste.objects.room_title import RoomTitle
from celeste.objects.spring import Spring
from celeste import game
from celeste import helper

# Maps sprite indices to game object
types = {PlayerSpawn.tile: PlayerSpawn,
         Key.tile: Key,
         Spring.tile: Spring,
         Chest.tile: Chest,
         Balloon.tile: Balloon,
         FallFloor.tile: FallFloor,
         Fruit.tile: Fruit,
         FlyFruit.tile: FlyFruit,
         FakeWall.tile: FakeWall,
         Message.tile: Message,
         BigChest.tile: BigChest,
         Flag.tile: Flag,
         }

def load_room(x,y):
    has_dashed=False
    has_key=False

    # reset object list
    game.objects = p8.platform.Group(max_size=43)
    game.objects.x = 16

    # current room
    game.room.x = x
    game.room.y = y

    # background map
    if p8.platform_id == "adafruit":
        game.objects.append(p8._map(game.room.x * 16,game.room.y * 16,0,0,16,16,4))


    if p8.platform_id == "adafruit":
        off = -4 if game.is_title() else 0
        game.objects.append(p8._map(game.room.x*16,game.room.y * 16,off,0,16,16,2))

    # entities
    for tx in range(16):
        for ty in range(16):
            tile = p8.mget(game.room.x*16+tx,game.room.y*16+ty)
            if tile==11 or tile == 12:
                direction = -1
                if tile == 12:
                    direction = 1
                p = Platform(x=tx*8, y=ty*8, direction=direction)
                game.objects.append(p)
                if Platform not in game.objects_by_type:
                    game.objects_by_type[Platform]
                game.objects_by_type[Platform].append(p)
            else:
                if tile in types:
                    game.objects.append(types[tile](x=tx*8, y=ty*8))

    if not game.is_title():
        game.objects.append(RoomTitle(x=0, y=0))
    else:
        # credits
        game.objects.append(p8._print("A+B",58,80,5))
        game.objects.append(p8._print("MATT THORSON",42,96,5))
        game.objects.append(p8._print("NOEL BERRY",46,102,5))

def title_screen():
    game.got_fruit = [False] * 30
    game.frames=0
    game.deaths=0
    game.max_djump=1
    game.start_game=False
    game.start_game_flash=0
    p8.music(40,0,7)

    load_room(7,3)

def begin_game():
    game.frames=0
    game.seconds=0
    game.minutes=0
    game.music_timer=0
    game.start_game=False
    p8.music(0,0,7)
    load_room(6,0)

def _update():
    game.frames=((game.frames+1)%30)
    if game.frames==0 and game.level_index()<30:
        game.seconds=((game.seconds+1)%60)
        if game.seconds==0:
            game.minutes+=1

    if game.music_timer>0:
        game.music_timer-=1
        if game.music_timer<=0:
            music(10,0,7)

    if game.sfx_timer>0:
        game.sfx_timer-=1

    # cancel if freeze
    if game.freeze>0:
        game.freeze-=1
        return

    # screenshake
    if game.shake>0:
        game.shake-=1
        p8.camera()
        if game.shake>0:
            p8.camera(-2+p8.rnd(5),-2+p8.rnd(5))

    # restart (soon)
    if game.will_restart and game.delay_restart>0:
        game.delay_restart-=1
        if game.delay_restart<=0:
            game.will_restart=False
            load_room(game.room.x,game.room.y)

    # update each object
    for obj in game.objects:
        obj.move(obj.spd.x,obj.spd.y)
        obj.update()

    # start game
    if game.is_title():
        if not game.start_game and (True or p8.btn(game.k_jump) or p8.btn(game.k_dash)):
            p8.music(-1)
            game.start_game_flash=50
            game.start_game=True
            p8.sfx(38)

        if game.start_game:
            game.start_game_flash-=1
            if game.start_game_flash<=-30:
                begin_game()

# drawing functions
def _draw():
    if game.freeze > 0:
        return

    # reset all palette values
    p8.pal()

    # start game flash
    if game.start_game:
        c = 10
        if game.start_game_flash > 10:
            if game.frames % 10 < 5:
                c = 7
        elif game.start_game_flash > 5:
            c = 2
        elif game.start_game_flash > 0:
            c = 1
        else:
            c = 0

        if c < 10:
            p8.pal(6, c)
            p8.pal(12, c)
            p8.pal(13, c)
            p8.pal(5, c)
            p8.pal(1, c)
            p8.pal(7, c)

    # clear screen
    bg_col = 0
    if game.flash_bg:
        bg_col = game.frames / 5
    elif game.new_bg:
        bg_col=2
    p8.rectfill(0,0,128,128,bg_col)

    display.show(game.objects)

    # clouds
    if not game.is_title():
        for c in clouds:
            c.draw()

    # draw bg terrain
    # if p8.platform == "adafruit":
    #     game.objects.append(p8._map(game.room.x * 16,game.room.y * 16,0,0,16,16,4))
    # else:
    #     p8._map(game.room.x * 16,game.room.y * 16,0,0,16,16,0)

    # platforms/big chest
    for o in game.objects:
        if isinstance(o, Platform) or isinstance(o, BigChest):
            o.draw()

    # draw terrain
    # off = -4 if game.is_title() else 0
    # if p8.platform == "adafruit":
    #     p8._map(game.room.x*16,game.room.y * 16,off,0,16,16,2)

    # draw objects
    for o in game.objects:
        if not isinstance(o, Platform) and not isinstance(o, BigChest):
            try:
                o.draw()
            except AttributeError:
                pass

    # draw fg terrain
    # if p8.platform != "gb" and platform != "gbc":
    #     p8._map(game.room.x * 16,game.room.y * 16,0,0,16,16,8)

    # particles
    for p in particles:
        p.draw()

    # dead particles
    for p in game.dead_particles:
        p.draw()

    # draw outside of the screen for screenshake
    p8.rectfill(-5,-5,-1,133,0)
    p8.rectfill(-5,-5,133,-1,0)
    p8.rectfill(-5,128,133,133,0)
    p8.rectfill(128,-5,133,133,0)

    if game.level_index() == 30:
        p = None
        for o in game.objects:
            if isinstance(o, Player):
                p = o
                break
        if p:
            diff=min(24,40-abs(p.x+4-64))
            rectfill(0,0,diff,128,0)
            rectfill(128-diff,0,128,128,0)

# displayio.release_displays()
# spi = busio.SPI(pin.PB13, pin.PB15)
# bus = displayio.FourWire(spi, command=pin.PB05, chip_select=pin.PB07, reset=pin.PA01)
# display = adafruit_st7735r.ST7735R(bus, width=160, height=128, backlight_pin=pin.PA00, rotation=270)

if p8.platform_id == "adafruit":
    display = board.DISPLAY
    display.auto_brightness = False
    display.brightness = 1
else:
    display = gb

print("code loaded:", time.monotonic() - last_checkpoint)
last_checkpoint = time.monotonic()
if p8.platform_id == "adafruit":
    p8.load_resources("celeste-original.p8")
elif p8.platform_id == "gb":
    p8.load_resources("celeste-gb.p8")
elif p8.platform_id == "gbc":
    p8.load_resources("celeste-gbc.p8")
print("resources loaded:", time.monotonic() - last_checkpoint)

clouds = []
for i in range(1): #is 16 normally
    clouds.append(Cloud(p8.rnd(128), p8.rnd(128), 1+p8.rnd(4), 32+p8.rnd(32)))

particles = []
for i in range(1): # was 24
    particles.append(Particle(p8.rnd(128), p8.rnd(128), 0+p8.flr(p8.rnd(5)/4), 0.25+p8.rnd(5), p8.rnd(1), 6+p8.flr(0.5+p8.rnd(1))))

# entry point
title_screen()

def print_recursive(o, indent=0):
    print("  "*indent + str(o), o.x, o.y)
    if not isinstance(o, p8.platform.Group):
        return
    for element in o:
        print_recursive(element, indent=indent+1)

i = 0
#for _ in range(100):
while True:
    # print("tick", i)
    _update()
    _draw()
    p8.tick(display, None)
    #print_recursive(game.objects)
    # print()
    i += 1
