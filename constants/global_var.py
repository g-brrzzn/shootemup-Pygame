import pygame


class Configs:
    def __init__(self):
        FHD =   (1920, 1080)
        HD =    (1280, 720)
        XGA =   (1024, 768)
        QHD =   (960, 540)
        SVGA =  (800, 600)
        self.RESOLUTIONS = [SVGA, QHD, XGA, HD, FHD]
        self.SHOW_FPS = False
        self.SET_FULLSCREEN = True
        self.WINDOW_SIZE = self.RESOLUTIONS[4]

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
SCALED_SPRITE_SIZE = SPRITE_SIZE * 4

MAX_LIFE = 3

BACKGROUND_COLOR_1 = (15, 25, 27, 200)
BACKGROUND_COLOR_2 = (15, 25, 27, 200)

GAME_COLOR = (100, 40, 80)

BACKGROUND_COLOR_GAME_1 = (BACKGROUND_COLOR_1[0], BACKGROUND_COLOR_1[1], BACKGROUND_COLOR_1[2], 255)
BACKGROUND_COLOR_GAME_2 = (BACKGROUND_COLOR_2[0], BACKGROUND_COLOR_2[1], BACKGROUND_COLOR_2[2], 255)

BACKGROUND_COLOR_MENU_1 = (BACKGROUND_COLOR_1[0], BACKGROUND_COLOR_1[1], BACKGROUND_COLOR_1[2], 20)
BACKGROUND_COLOR_MENU_2 = (BACKGROUND_COLOR_2[0], BACKGROUND_COLOR_2[1], BACKGROUND_COLOR_2[2], 20)


CONTROLS = {
    'UP':       [pygame.K_w, pygame.K_UP],
    'DOWN':     [pygame.K_s, pygame.K_DOWN],
    'RIGHT':    [pygame.K_d, pygame.K_RIGHT],
    'LEFT':     [pygame.K_a, pygame.K_LEFT],
    'FIRE':     [pygame.K_SPACE],
    'START':    [pygame.K_RETURN, pygame.K_SPACE],
    'ESC':      [pygame.K_ESCAPE]
}
