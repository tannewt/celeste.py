# ~celeste~
# matt thorson + noel berry
# ported to python by scott shawcroft (@tannewt)
import ugame

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
    game.objects = []

    # current room
    game.room.x = x
    game.room.y = y

    # entities
    for tx in range(16):
        for ty in range(16):
            tile = p8.mget(game.room.x*16+tx,game.room.y*16+ty)
            if tile==11:
                game.objects.append(Platform(tx*8, ty*8, -1))
            elif tile==12:
                game.objects.append(Platform(tx*8, ty*8, 1))
            else:
                if tile in types:
                    game.objects.append(types[tile](tx*8,ty*8))

    if not game.is_title():
        game.objects.append(RoomTitle(0,0))

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
    global frames, seconds, minutes, music_timer, start_game
    game.frames=0
    game.seconds=0
    game.minutes=0
    game.music_timer=0
    game.start_game=False
    p8.music(0,0,7)
    load_room(0,0)

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
        camera()
        if game.shake>0:
            camera(-2+rnd(5),-2+rnd(5))

    # restart (soon)
    if game.will_restart and game.delay_restart>0:
        game.delay_restart-=1
        if game.delay_restart<=0:
            game.will_restart=false
            load_room(game.room.x,game.room.y)

    # update each object
    for obj in game.objects:
        obj.move(obj.spd.x,obj.spd.y)
        obj.update()

    # start game
    if game.is_title():
        if not game.start_game and (p8.btn(game.k_jump) or p8.btn(game.k_dash)):
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

    # clouds
    if not game.is_title():
        for c in clouds:
            c.draw()

    # draw bg terrain
    p8._map(game.room.x * 16,game.room.y * 16,0,0,16,16,4)

    # platforms/big chest
    for o in game.objects:
        if isinstance(o, Platform) or isinstance(o, BigChest):
            o.draw()

    # draw terrain
    off = -4 if game.is_title() else 0
    p8._map(game.room.x*16,game.room.y * 16,off,0,16,16,2)

    # draw objects
    for o in game.objects:
        if not isinstance(o, Platform) and not isinstance(o, BigChest):
            o.draw()

    # draw fg terrain
    p8._map(game.room.x * 16,game.room.y * 16,0,0,16,16,8)

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

    # credits
    if game.is_title():
        p8._print("x+c",58,80,5)
        p8._print("matt thorson",42,96,5)
        p8._print("noel berry",46,102,5)

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

p8.load_resources("celeste-original.p8")

clouds = []
for i in range(16):
    clouds.append(Cloud(p8.rnd(128), p8.rnd(128), 1+p8.rnd(4), 32+p8.rnd(32)))

particles = []
for i in range(24):
    particles.append(Particle(p8.rnd(128), p8.rnd(128), 0+flr(p8.rnd(5)/4), 0.25+rnd(5), rnd(1), 6+flr(0.5+rnd(1))))

# entry point
title_screen()

i = 0
#for i in range(81):
while True:
    print("tick", i)
    _update()
    _draw()
    p8.tick(ugame.display, ugame.buttons.get_pressed())
    print()
    i += 1
