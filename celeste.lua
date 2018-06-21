-- ~celeste~
-- matt thorson + noel berry

-- globals --
-------------

room = { x=0, y=0 }
objects = {}
types = {}
freeze=0
shake=0
will_restart=false
delay_restart=0
got_fruit={}
has_dashed=false
sfx_timer=0
has_key=false
pause_player=false
flash_bg=false
music_timer=0

k_left=0
k_right=1
k_up=2
k_down=3
k_jump=4
k_dash=5

-- entry point --
-----------------

function _init()
    title_screen()
end

function title_screen()
    got_fruit = {}
    for i=0,29 do
        add(got_fruit,false) end
    frames=0
    deaths=0
    max_djump=1
    start_game=false
    start_game_flash=0
    music(40,0,7)

    load_room(7,3)
end




-- effects --
-------------

clouds = {}
for i=0,16 do
    add(clouds,{
        x=rnd(128),
        y=rnd(128),
        spd=1+rnd(4),
        w=32+rnd(32)
    })
end

particles = {}
for i=0,24 do
    add(particles,{
        x=rnd(128),
        y=rnd(128),
        s=0+flr(rnd(5)/4),
        spd=0.25+rnd(5),
        off=rnd(1),
        c=6+flr(0.5+rnd(1))
    })
end

dead_particles = {}

psfx=function(num)
 if sfx_timer<=0 then
  sfx(num)
 end
end

create_hair=function(obj)
    obj.hair={}
    for i=0,4 do
        add(obj.hair,{x=obj.x,y=obj.y,size=max(1,min(2,3-i))})
    end
end

set_hair_color=function(djump)
    pal(8,(djump==1 and 8 or djump==2 and (7+flr((frames/3)%2)*4) or 12))
end

draw_hair=function(obj,facing)
    local last={x=obj.x+4-facing*2,y=obj.y+(btn(k_down) and 4 or 3)}
    foreach(obj.hair,function(h)
        h.x+=(last.x-h.x)/1.5
        h.y+=(last.y+0.5-h.y)/1.5
        circfill(h.x,h.y,h.size,8)
        last=h
    end)
end

unset_hair_color=function()
    pal(8,8)
end




function break_spring(obj)
    obj.hide_in=15
end





function break_fall_floor(obj)
 if obj.state==0 then
     psfx(15)
        obj.state=1
        obj.delay=15--how long until it falls
        init_object(smoke,obj.x,obj.y)
        local hit=obj.collide(spring,0,-1)
        if hit~=nil then
            break_spring(hit)
        end
    end
end


-- object functions --
-----------------------

function destroy_object(obj)
    del(objects,obj)
end

function kill_player(obj)
    sfx_timer=12
    sfx(0)
    deaths+=1
    shake=10
    destroy_object(obj)
    dead_particles={}
    for dir=0,7 do
        local angle=(dir/8)
        add(dead_particles,{
            x=obj.x+4,
            y=obj.y+4,
            t=10,
            spd={
                x=sin(angle)*3,
                y=cos(angle)*3
            }
        })
        restart_room()
    end
end

-- room functions --
--------------------

function restart_room()
    will_restart=true
    delay_restart=15
end

function next_room()
 if room.x==2 and room.y==1 then
  music(30,500,7)
 elseif room.x==3 and room.y==1 then
  music(20,500,7)
 elseif room.x==4 and room.y==2 then
  music(30,500,7)
 elseif room.x==5 and room.y==3 then
  music(30,500,7)
 end

    if room.x==7 then
        load_room(0,room.y+1)
    else
        load_room(room.x+1,room.y)
    end
end

function draw_time(x,y)

    local s=seconds
    local m=minutes%60
    local h=flr(minutes/60)

    rectfill(x,y,x+32,y+6,0)
    print((h<10 and "0"..h or h)..":"..(m<10 and "0"..m or m)..":"..(s<10 and "0"..s or s),x+1,y+1,7)

end

-- helper functions --
----------------------

function clamp(val,a,b)
    return max(a, min(b, val))
end

function appr(val,target,amount)
 return val > target
     and max(val - amount, target)
     or min(val + amount, target)
end

function maybe()
    return rnd(1)<0.5
end

function solid_at(x,y,w,h)
 return tile_flag_at(x,y,w,h,0)
end

function ice_at(x,y,w,h)
 return tile_flag_at(x,y,w,h,4)
end

function tile_flag_at(x,y,w,h,flag)
 for i=max(0,flr(x/8)),min(15,(x+w-1)/8) do
     for j=max(0,flr(y/8)),min(15,(y+h-1)/8) do
         if fget(tile_at(i,j),flag) then
             return true
         end
     end
 end
    return false
end

function tile_at(x,y)
 return mget(room.x * 16 + x, room.y * 16 + y)
end

function spikes_at(x,y,w,h,xspd,yspd)
 for i=max(0,flr(x/8)),min(15,(x+w-1)/8) do
     for j=max(0,flr(y/8)),min(15,(y+h-1)/8) do
      local tile=tile_at(i,j)
      if tile==17 and ((y+h-1)%8>=6 or y+h==j*8+8) and yspd>=0 then
       return true
      elseif tile==27 and y%8<=2 and yspd<=0 then
       return true
         elseif tile==43 and x%8<=2 and xspd<=0 then
          return true
         elseif tile==59 and ((x+w-1)%8>=6 or x+w==i*8+8) and xspd>=0 then
          return true
         end
     end
 end
    return false
end
