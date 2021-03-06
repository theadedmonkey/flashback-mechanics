import sys, pygame, json
from pygame.locals import *

from pprint import pprint

def group_by_animation_name(frames):
    animations = {}
    for frame in frames:
        if frame.name_group not in animations:
            animations[frame.name_group] = []
        animations[frame.name_group].append(frame)

    return animations

def parse_frame_data():
    with open('assets/dst/atlas.json') as frame_file:
        frame_data = json.load(frame_file)

    frames = [];
    for frame_item in frame_data['frames']:
         frame_name = frame_item['filename'].split('/')[1]
         frame_name_group = frame_item['filename'].split('/')[0]
         frame_srcRect = pygame.Rect(
           frame_item['frame']['x'],
           frame_item['frame']['y'],
           frame_item['frame']['w'],
           frame_item['frame']['h'],
          )
         frame_dstRect = pygame.Rect(
           frame_item['spriteSourceSize']['x'],
           frame_item['spriteSourceSize']['y'],
           frame_item['spriteSourceSize']['w'],
           frame_item['spriteSourceSize']['h'],
         )

         frames.append(Frame(frame_name, frame_name_group, frame_srcRect, frame_dstRect))

    return frames

class Frame(object):

    def __init__(self, name, name_group, srcRect, dstRect):
        self.name = name
        self.name_group = name_group
        self.srcRect = srcRect
        self.dstRect = dstRect

class Animation(object):

    def __init__(self, name, frames):
        self.name = name
        self.frames = frames
        self.frame_count = len(self.frames)
        self.frame_last_idx = 0 if self.frame_count == 0 else self.frame_count - 1

class AnimationPlayer(object):

    def __init__(self, animation):
        self.animation = animation
        self.frame_idx = 0
        self.frame_current = animation.frames[self.frame_idx]
        self.has_finish = False

        self.tick_duration = 60
        self.tick_current = 0
        self.tick_last = 0
        self.tick_accum = 0

    def update(self):
        # unblock input while 2 last frames of animation
        if self.frame_idx > self.animation.frame_last_idx - 2:
	        is_input_blocked = False

        self.frame_current = self.animation.frames[self.frame_idx]

        self.tick_current = pygame.time.get_ticks()
        self.tick_accum += self.tick_current - self.tick_last

        if self.tick_accum > self.tick_duration:
            if self.frame_idx == self.animation.frame_last_idx:
                self.has_finish = True
            else:
                self.frame_idx += 1

            self.tick_accum -= self.tick_duration

        self.tick_last = self.tick_current

    def set_animation(self, animation):
        self.animation = animation
        self.frame_idx = 0
        self.tick_accum = 0
        is_input_blocked = True
        self.has_finish = False

# set up pygame
pygame.init()

# set up screen size
SCREEN_WIDTH = 1024;
SCREEN_WIDTH_HALF = SCREEN_WIDTH / 2;

SCREEN_HEIGHT = 896;
SCREEN_HEIGHT_HALF = SCREEN_HEIGHT / 2;

# set up the boad
TILE_SIZE = 32
COLS_COUNT = 32
ROWS_COUNT = 28
board = [[0 for _ in range(COLS_COUNT)] for _ in range(ROWS_COUNT)]

# set up the colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

# set up input
is_input_blocked = False

# set up character
conrad_x = 0;
conrad_y = 8;
conrad_state = 'IDLE'

# set up the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Flashback')

#set up the background
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill(COLOR_WHITE)

# set up the atlas
atlasSurface = pygame.image.load('assets/dst/atlas.png').convert_alpha()

#set up animations
animations = group_by_animation_name(parse_frame_data())
animation_next = None
animation_idle = Animation('idle-0', animations['idle-0'])
animation_step_0 = Animation('step-0', animations['step-0'])
animation_step_1 = Animation('step-1', animations['step-1'])
animation_current = animation_idle
animation_player = AnimationPlayer(animation_current)

def draw_grid():
    x = 0
    y = 0
    min_x = 0
    min_y = 0
    max_x = TILE_SIZE * COLS_COUNT
    max_y = TILE_SIZE * ROWS_COUNT

    for row in range(ROWS_COUNT):
        y = TILE_SIZE * row
        pygame.draw.line(screen, COLOR_BLACK, (min_x, y), (max_x, y), 1)
        for col in range(COLS_COUNT):
            x = TILE_SIZE * col
            pygame.draw.line(screen, COLOR_BLACK, (x, min_y), (x, max_y), 1)

def draw_conrad():
    srcRect = animation_player.frame_current.srcRect
    dstRect = animation_player.frame_current.dstRect

    dstRect.x = TILE_SIZE * conrad_x
    dstRect.y = TILE_SIZE * conrad_y

    screen.blit(atlasSurface, dstRect, srcRect)

# run the game loop
while True:
    animation_next = animation_idle
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if not is_input_blocked:
        if keys[K_d]:
            if animation_player.animation.name == 'idle-0':
                animation_next = animation_step_0
            if animation_player.animation.name == 'step-0':
                animation_next = animation_step_1
            if animation_player.animation.name == 'step-1':
                animation_next = animation_step_0

    if animation_player.has_finish:
        if animation_player.animation.name == 'step-0':
            conrad_x += 2
        if animation_player.animation.name == 'step-1':
            conrad_x += 2
        if animation_player.animation.name != animation_next.name:
            animation_player.set_animation(animation_next)


    animation_player.update()

    screen.fill(COLOR_WHITE)
    draw_grid()
    draw_conrad()


    pygame.display.flip()
