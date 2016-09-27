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
    with open('assets/dst/full/atlas.json') as frame_file:
        frame_data = json.load(frame_file)

    frames = [];
    for frame_item in frame_data['frames']:
         frame_name = frame_item['filename'].split('/')[1]
         frame_name_group = frame_item['filename'].split('/')[0]
         frame_rect_src = pygame.Rect(
           frame_item['frame']['x'],
           frame_item['frame']['y'],
           frame_item['frame']['w'],
           frame_item['frame']['h'],
          )
         frame_rect_dst = pygame.Rect(
           frame_item['spriteSourceSize']['x'],
           frame_item['spriteSourceSize']['y'],
           frame_item['spriteSourceSize']['w'],
           frame_item['spriteSourceSize']['h'],
         )

         frames.append(Frame(frame_name, frame_name_group, frame_rect_src, frame_rect_dst))

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

        self.has_reversed = False

    def reverse(self):
        self.frames = list(reversed(self.frames))
        self.has_reversed = not self.has_reversed

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

    def set_animation(self, animation, reverse=False):

        if reverse == True and animation.has_reversed == False:
            animation.reverse()
        elif reverse == False and animation.has_reversed == True:
            animation.reverse()

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

# set up the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Flashback')

# set up the atlas
atlasSurface = pygame.image.load('assets/dst/full/atlas.png').convert_alpha()

#set up animations
animations = group_by_animation_name(parse_frame_data())
animation_idle = Animation('idle-0', animations['idle-0'])
animation_step_0 = Animation('step-0', animations['step-0'])
animation_step_1 = Animation('step-1', animations['step-1'])
animation_turn = Animation('turn-0', animations['turn-0'])
animation_duck = Animation('duck-0', animations['duck-0'])
animation_fall = Animation('fall-0', animations['fall-0'])
animation_player = AnimationPlayer(animation_idle)

class StateStanding(object):

    def __init__(self):
        pass

    def enter(self, conrad):
        animation_player.set_animation(animation_idle)

    def exit(self, conrad):
        pass

    def handle_event(self, conrad, event):
        if not is_input_blocked:
            if event[K_d]:
                if conrad.direction == 'RIGHT':
                    conrad.state = Conrad.state_step_0
                if conrad.direction == 'LEFT':
                    conrad.state = Conrad.state_turn

            if event[K_a]:
                if conrad.direction == 'RIGHT':
                    conrad.state = Conrad.state_turn
                if conrad.direction == 'LEFT':
                    conrad.state = Conrad.state_step_0

            if event[K_s]:
                conrad.state = Conrad.state_duck


    def update(self, conrad):
        pass

class StateStep0(object):

    def __init__(self):
        self.__state_next = None

    def enter(self, conrad):
        animation_player.set_animation(animation_step_0)

        if conrad.direction == 'LEFT':
            conrad.x -= 2

    def exit(self, conrad):
        if conrad.direction == 'RIGHT':
            conrad.x += 2

    def handle_event(self, conrad, event):
        self.__state_next = Conrad.state_standing

        if not is_input_blocked:
            if event[K_d]:
                if conrad.direction == 'RIGHT':
                    self.__state_next = Conrad.state_step_1
                if conrad.direction == 'LEFT':
                    self.__state_next = Conrad.state_turn
            if event[K_a]:
                if conrad.direction == 'RIGHT':
                    self.__state_next = Conrad.state_turn
                if conrad.direction == 'LEFT':
                    self.__state_next = Conrad.state_step_1

        if animation_player.has_finish:
            conrad.state = self.__state_next
            # self.exit(conrad)

    def update(self, conrad):
        pass

class StateStep1(object):

    def __init__(self):
        self.__state_next = None

    def enter(self, conrad):
        animation_player.set_animation(animation_step_1)

        if conrad.direction == 'LEFT':
            conrad.x -= 2

    def exit(self, conrad):
        if conrad.direction == 'RIGHT':
            conrad.x += 2

    def handle_event(self, conrad, event):
        self.__state_next = Conrad.state_standing

        if not is_input_blocked:
            if event[K_d]:
                if conrad.direction == 'RIGHT':
                    self.__state_next = Conrad.state_step_0
                if conrad.direction == 'LEFT':
                    self.__state_next = Conrad.state_turn
            if event[K_a]:
                if conrad.direction == 'RIGHT':
                    self.__state_next = Conrad.state_turn
                if conrad.direction == 'LEFT':
                    self.__state_next = Conrad.state_step_0

        if animation_player.has_finish:
            conrad.state = self.__state_next
            # self.exit(conrad)

    def update(self, conrad):
        pass

class StateTurn(object):

    def __init__(self):
        self.__animation_next = None

    def enter(self, conrad):
        animation_player.set_animation(animation_turn)

    def exit(self, conrad):
        conrad.direction = 'LEFT' if conrad.direction == 'RIGHT' else 'RIGHT'

    def handle_event(self, conrad, event):
        if animation_player.has_finish:
            conrad.state = Conrad.state_standing
            # self.exit(conrad)

    def update(self, conrad):
        pass

class StateDuck(object):

    def __init__(self):
        pass

    def enter(self, conrad):
        animation_player.set_animation(animation_duck)

    def exit(self, conrad):
        pass

    def handle_event(self, conrad, event):
        if animation_player.has_finish:
            if not event[K_s]:
                conrad.state = Conrad.state_stand_up
                # self.exit(conrad)

    def update(self, conrad):
        pass

class StateStandUp(object):

    def __init__(self):
        pass

    def enter(self, conrad):
        animation_player.set_animation(animation_duck, reverse=True)

    def exit(self, conrad):
        pass

    def handle_event(self, conrad, event):
        if animation_player.has_finish:
            conrad.state = Conrad.state_standing
            # self.exit(conrad)

    def update(self, conrad):
        pass

class StateFall(object):

    def __init__(self):
        pass

    def enter(self, conrad):
        animation_player.set_animation(animation_fall)
        if conrad.direction == 'LEFT':
            conrad.x -= 3

    def exit(self, conrad):
        if conrad.direction == 'RIGHT':
            conrad.x += 2
        if conrad.direction == 'LEFT':
            conrad.x += 1

        conrad.y += 9


    def handle_event(self, conrad, event):
        if animation_player.has_finish:
            conrad.state = Conrad.state_standing
            # self.exit(conrad)

    def update(self, conrad):
        pass

class Conrad(object):

    state_standing = StateStanding()
    state_step_0 = StateStep0()
    state_step_1 = StateStep1()
    state_turn = StateTurn()
    state_duck = StateDuck()
    state_stand_up = StateStandUp()
    state_fall = StateFall()

    def __init__(self):
        self.x = 8
        self.y = 0
        self.direction = 'LEFT'
        self.__state = Conrad.state_standing

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state.exit(self)
        self.__state = state
        self.__state.enter(self)

    def handle_event(self, event):
        self.state.handle_event(self, event)

    def update(self):
        self.state.update(self)

# set up character
conrad = Conrad()

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

    dstRect.x = TILE_SIZE * conrad.x
    dstRect.y = TILE_SIZE * conrad.y

    sur = pygame.Surface(srcRect.size).convert()
    sur.blit(atlasSurface, (0, 0), srcRect)
    color_key = sur.get_at((0, 0))
    sur.set_colorkey(color_key, pygame.RLEACCEL)

    a = sur
    if conrad.direction == 'LEFT':
        a = pygame.transform.flip(sur, True, False)

    # draw borders
    min_x = dstRect.x
    min_y = dstRect.y
    max_x = min_x + dstRect.w
    max_y = min_y + dstRect.h

    point_list = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]



    screen.blit(a, dstRect)
    pygame.draw.lines(screen, COLOR_RED, True, point_list, 2)
    # screen.blit(atlasSurface, dstRect, srcRect)

# run the game loop
while True:
    animation_next = animation_idle
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()


    conrad.handle_event(keys)
    conrad.update()
    animation_player.update()

    screen.fill(COLOR_WHITE)
    draw_grid()
    draw_conrad()

    pygame.display.flip()
