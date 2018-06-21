class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
room = Room(x=0, y=0)
objects = []
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
particles = []
dead_particles = []
clouds = []
seconds = 0
minutes = 0
max_djump = 1

k_left=0
k_right=1
k_up=2
k_down=1
k_jump=7
k_dash=6


def level_index():
    return room.x%8+room.y*8

def is_title():
    return level_index()==31
