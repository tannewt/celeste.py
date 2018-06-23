import math

from celeste import game
from celeste import geom

from celeste.effects.dead_particle import DeadParticle

from .celeste_object import CelesteObject
from .smoke import Smoke
from celeste import helper

import pico8 as p8

class Player(CelesteObject):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.p_jump=False
        self.p_dash=False
        self.grace=0
        self.jbuffer=0
        self.djump=game.max_djump
        self.dash_time=0
        self.dash_effect_time=0
        self.dash_target=geom.Vec(x=0,y=0)
        self.dash_accel=geom.Vec(x=0,y=0)
        self.hitbox = geom.Rect(x=1,y=3,w=6,h=5)
        self.spr_off=0
        self.was_on_ground=False
        helper.create_hair(self)

    def _die(self):
        game.sfx_timer=12
        p8.sfx(0)
        game.deaths+=1
        game.shake=10
        game.objects.remove(self)
        game.dead_particles=[]
        for dir in range(8):
            angle=(dir/8)
            game.dead_particles.append(DeadParticle(self.x+4,
                                                    self.y+4,
                                                    10,
                                                    geom.Vec(x=math.sin(angle)*3,
                                                             y=math.cos(angle)*3)))
            game.restart_room()

    def _spike_collide(self):
        x = self.x + self.hitbox.x
        y = self.y + self.hitbox.y
        w = self.hitbox.w
        h = self.hitbox.h
        xspd = self.spd.x
        yspd = self.spd.y
        for i in range(max(0,x//8), min(16,(x+w-1)//8+1)):
            for j in range(max(0,y//8), min(16,(y+h-1)//8+1)):
                tile = p8.mget(game.room.x * 16 + i, game.room.y * 16 + j)
                if tile==17 and ((y+h-1)%8>=6 or y+h==j*8+8) and yspd>=0:
                    return True
                elif tile==27 and y%8<=2 and yspd<=0:
                    return True
                elif tile==43 and x%8<=2 and xspd<=0:
                    return True
                elif tile==59 and ((x+w-1)%8>=6 or x+w==i*8+8) and xspd>=0:
                    return True
        return False

    def update(self):
        if game.pause_player:
            return

        input = p8.btn(game.k_right) and 1 or (p8.btn(game.k_left) and -1 or 0)

        # spikes collide
        if self._spike_collide():
            self._die()

        # bottom death
        if self.y>128:
            self._die()

        on_ground=self._is_solid(0,1)
        on_ice=self._is_ice(0,1)

        # smoke particles
        if on_ground and not self.was_on_ground:
            game.objects.append(Smoke(self.x,self.y+4))

        jump = p8.btn(game.k_jump) and not self.p_jump
        self.p_jump = p8.btn(game.k_jump)
        if jump:
            self.jbuffer=4
        elif self.jbuffer>0:
            self.jbuffer-=1

        dash = p8.btn(game.k_dash) and not self.p_dash
        self.p_dash = p8.btn(game.k_dash)

        if on_ground:
            self.grace=6
            if self.djump<game.max_djump:
                game.psfx(54)
                self.djump=game.max_djump
        elif self.grace > 0:
            self.grace-=1

        self.dash_effect_time -=1
        if self.dash_time > 0:
            game.objects.append(Smoke(self.x,self.y))
            self.dash_time-=1
            self.spd.x=helper.appr(self.spd.x,self.dash_target.x,self.dash_accel.x)
            self.spd.y=helper.appr(self.spd.y,self.dash_target.y,self.dash_accel.y)
        else:
            # move
            maxrun=1
            accel=0.6
            deccel=0.15

            if not on_ground:
                accel=0.4
            elif on_ice:
                accel=0.05
                if input==(-1 if self.flip.x else 1):
                    accel=0.05

            if abs(self.spd.x) > maxrun:
                self.spd.x=helper.appr(self.spd.x,helper.sign(self.spd.x)*maxrun,deccel)
            else:
                self.spd.x=helper.appr(self.spd.x,input*maxrun,accel)

            # facing
            if self.spd.x!=0:
                self.flip.x=(self.spd.x<0)

            # gravity
            maxfall=2
            gravity=0.21

            if abs(self.spd.y) <= 0.15:
                gravity*=0.5

            # wall slide
            if input!=0 and self._is_solid(input,0) and not self._is_ice(input,0):
                maxfall=0.4
                if p8.rnd(10)<2:
                    game.objects.append(Smoke(self.x+input*6,self.y))

            if not on_ground:
                self.spd.y=helper.appr(self.spd.y,maxfall,gravity)

            # jump
            if self.jbuffer>0:
                if self.grace>0:
                    # normal jump
                    game.psfx(1)
                    self.jbuffer=0
                    self.grace=0
                    self.spd.y=-2
                    game.objects.append(Smoke(self.x,self.y+4))
                else:
                    # wall jump
                    wall_dir = 0
                    if self._is_solid(-3,0):
                        wall_dir = -1
                    elif self._is_solid(3,0):
                        wall_dir = 1
                    if wall_dir!=0:
                        game.psfx(2)
                        self.jbuffer=0
                        self.spd.y=-2
                        self.spd.x=-wall_dir*(maxrun+1)
                        if not self._is_ice(wall_dir*3,0):
                            game.objects.append(Smoke(self.x+wall_dir*6,self.y))

            # dash
            d_full=5
            d_half=d_full*0.70710678118

            if self.djump>0 and dash:
                game.objects.append(Smoke(self.x,self.y))
                self.djump-=1
                self.dash_time=4
                game.has_dashed=True
                self.dash_effect_time=10
                v_input = 0
                if p8.btn(game.k_up):
                    v_input = -1
                elif p8.btn(game.k_down):
                    v_input = 1
                if input!=0:
                    if v_input!=0:
                        self.spd.x=input*d_half
                        self.spd.y=v_input*d_half
                    else:
                        self.spd.x=input*d_full
                        self.spd.y=0
                elif v_input!=0:
                    self.spd.x=0
                    self.spd.y=v_input*d_full
                else:
                    self.spd.x=(-1 if self.flip.x else 1)
                    self.spd.y=0

                game.psfx(3)
                game.freeze=2
                game.shake=6
                self.dash_target.x=2*helper.sign(self.spd.x)
                self.dash_target.y=2*helper.sign(self.spd.y)
                self.dash_accel.x=1.5
                self.dash_accel.y=1.5

                if self.spd.y<0:
                    self.dash_target.y*=.75

                if self.spd.y!=0:
                    self.dash_accel.x*=0.70710678118

                if self.spd.x!=0:
                    self.dash_accel.y*=0.70710678118
            elif dash and self.djump<=0:
                game.psfx(9)
                game.objects.append(Smoke(self.x,self.y))

        # animation
        self.spr_off+=0.25
        if not on_ground:
            if self._is_solid(input,0):
                self.spr=5
            else:
                self.spr=3
        elif p8.btn(game.k_down):
            self.spr=6
        elif p8.btn(game.k_up):
            self.spr=7
        elif (self.spd.x==0) or (not p8.btn(game.k_left) and not p8.btn(game.k_right)):
            self.spr=1
        else:
            self.spr=1+self.spr_off%4

        # next level
        if self.y<-4 and game.level_index()<30:
            game.next_room()

        # was on the ground
        self.was_on_ground=on_ground

    def draw(self):
        # clamp in screen
        if self.x<-1 or self.x>121:
            self.x=helper.clamp(self.x,-1,121)
            self.spd.x=0

        helper.set_hair_color(self.djump)
        helper.draw_hair(self,-1 if self.flip.x else 1)
        p8.spr(self.spr,self.x,self.y,1,1,self.flip.x,self.flip.y)
        helper.unset_hair_color()
