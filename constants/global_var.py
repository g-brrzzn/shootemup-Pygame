import pygame


class Configs:
    def __init__(self):
        UHD  =  (3840, 2160) # 5
        WQHD =  (2560, 1440) # 4
        FHD  =  (1920, 1080) # 3
        HD   =  (1280, 720)  # 2
        XGA  =  (1024, 768)  # 1
        QHD  =  (960, 540)   # 0
        self.RESOLUTIONS = [QHD, XGA, HD, FHD, WQHD, UHD]
        self.INTERNAL_RESOLUTION = (1600, 900)
        
        self.SHOW_FPS = False
        self.SET_FULLSCREEN = False
        self.WINDOW_SIZE = self.RESOLUTIONS[2]     

    @property
    def show_fps(self):
        return self.SHOW_FPS

    @show_fps.setter
    def show_fps(self, show):
        self.SHOW_FPS = bool(show)

    @property
    def set_fullscreen(self):
        return self.SET_FULLSCREEN

    @set_fullscreen.setter
    def set_fullscreen(self, set):
        self.SET_FULLSCREEN = bool(set)

    @property
    def window_size(self):
        return self.WINDOW_SIZE

    @window_size.setter
    def window_size(self, size):
        self.WINDOW_SIZE = size


config = Configs()

FRAME_RATE = 75
SPRITE_SIZE = 16
SCALE = 4
SCALED_SPRITE_SIZE = SPRITE_SIZE * SCALE

MAX_LIFE = 3

BACKGROUND_COLOR = (15, 25, 27, 200)
BACKGROUND_COLOR_1 = BACKGROUND_COLOR
BACKGROUND_COLOR_2 = BACKGROUND_COLOR

#GREEN = (57, 194, 163)
#PINK = (255, 113, 206)
GAME_COLOR = (100, 40, 80)

BACKGROUND_COLOR_GAME_1 = (BACKGROUND_COLOR_1[0], BACKGROUND_COLOR_1[1], BACKGROUND_COLOR_1[2], 255)
BACKGROUND_COLOR_GAME_2 = (BACKGROUND_COLOR_2[0], BACKGROUND_COLOR_2[1], BACKGROUND_COLOR_2[2], 255)

BACKGROUND_COLOR_MENU_1 = (BACKGROUND_COLOR_1[0], BACKGROUND_COLOR_1[1], BACKGROUND_COLOR_1[2], 20)
BACKGROUND_COLOR_MENU_2 = (BACKGROUND_COLOR_2[0], BACKGROUND_COLOR_2[1], BACKGROUND_COLOR_2[2], 20)

TITLE_YELLOW_1 =     (221, 245, 154)
TITLE_YELLOW_2 =     (185, 174, 115)
PLAYER_COLOR_GREEN = (28, 162, 111)


CONTROLS = {
    'UP':       [pygame.K_w, pygame.K_UP],
    'DOWN':     [pygame.K_s, pygame.K_DOWN],
    'RIGHT':    [pygame.K_d, pygame.K_RIGHT],
    'LEFT':     [pygame.K_a, pygame.K_LEFT],
    'FIRE':     [pygame.K_SPACE],
    'START':    [pygame.K_RETURN, pygame.K_SPACE],
    'ESC':      [pygame.K_ESCAPE]
}
