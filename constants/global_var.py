import pygame
import json
import os

CONFIG_FILE = "settings.json"


class Configs:
    def __init__(self):
        self.UHD = (3840, 2160)
        self.WQHD = (2560, 1440)
        self.FHD = (1920, 1080)
        self.HD = (1280, 720)
        self.XGA = (1024, 768)
        self.QHD = (960, 540)
        self.RESOLUTIONS = [self.QHD, self.XGA, self.HD, self.FHD, self.WQHD, self.UHD]
        self.INTERNAL_RESOLUTION = (1600, 900)

        self.SHOW_FPS = False
        self.SET_FULLSCREEN = False
        self.USE_OPENGL = True
        self.WINDOW_SIZE = self.HD
        self.APPLY_CONTROLLER_VIBRATION = True
        self.USE_ANALOG_STICK = True

        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    data = json.load(f)
                    self.SHOW_FPS = data.get("show_fps", self.SHOW_FPS)
                    self.SET_FULLSCREEN = data.get("fullscreen", self.SET_FULLSCREEN)
                    self.USE_OPENGL = data.get("use_opengl", self.USE_OPENGL)
                    win_size = data.get("window_size", self.WINDOW_SIZE)
                    self.APPLY_CONTROLLER_VIBRATION = data.get(
                        "apply_controller_vibration", self.APPLY_CONTROLLER_VIBRATION
                    )
                    self.USE_ANALOG_STICK = data.get("use_analog_stick", self.USE_ANALOG_STICK)
                    self.WINDOW_SIZE = tuple(win_size)
                except:
                    pass

    def save(self):
        data = {
            "show_fps": self.SHOW_FPS,
            "fullscreen": self.SET_FULLSCREEN,
            "use_opengl": self.USE_OPENGL,
            "window_size": self.WINDOW_SIZE,
            "apply_controller_vibration": self.APPLY_CONTROLLER_VIBRATION,
            "use_analog_stick": self.USE_ANALOG_STICK,
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

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
    def use_opengl(self):
        return self.USE_OPENGL

    @use_opengl.setter
    def use_opengl(self, use):
        self.USE_OPENGL = bool(use)

    @property
    def window_size(self):
        return self.WINDOW_SIZE

    @window_size.setter
    def window_size(self, size):
        self.WINDOW_SIZE = size

    @property
    def apply_controller_vibration(self):
        return self.APPLY_CONTROLLER_VIBRATION

    @apply_controller_vibration.setter
    def apply_controller_vibration(self, apply):
        self.APPLY_CONTROLLER_VIBRATION = bool(apply)
        
    @property
    def use_analog_stick(self):
        return self.USE_ANALOG_STICK

    @use_analog_stick.setter
    def use_analog_stick(self, apply):
        self.USE_ANALOG_STICK = bool(apply)


config = Configs()

FRAME_RATE = 75
SPRITE_SIZE = 16
SCALE = 4
SCALED_SPRITE_SIZE = SPRITE_SIZE * SCALE

MAX_LIFE = 3

BACKGROUND_COLOR = (15, 25, 27, 200)
BACKGROUND_COLOR_1 = BACKGROUND_COLOR
BACKGROUND_COLOR_2 = BACKGROUND_COLOR

# GREEN = (57, 194, 163)
# PINK = (255, 113, 206)
GAME_COLOR = (100, 40, 80)

BACKGROUND_COLOR_GAME_1 = (
    BACKGROUND_COLOR_1[0],
    BACKGROUND_COLOR_1[1],
    BACKGROUND_COLOR_1[2],
    255,
)
BACKGROUND_COLOR_GAME_2 = (
    BACKGROUND_COLOR_2[0],
    BACKGROUND_COLOR_2[1],
    BACKGROUND_COLOR_2[2],
    255,
)

BACKGROUND_COLOR_MENU_1 = (
    BACKGROUND_COLOR_1[0],
    BACKGROUND_COLOR_1[1],
    BACKGROUND_COLOR_1[2],
    20,
)
BACKGROUND_COLOR_MENU_2 = (
    BACKGROUND_COLOR_2[0],
    BACKGROUND_COLOR_2[1],
    BACKGROUND_COLOR_2[2],
    20,
)

TITLE_YELLOW_1 = (221, 245, 154)
TITLE_YELLOW_2 = (185, 174, 115)
PLAYER_COLOR_GREEN = (28, 162, 111)

CONTROLS = {
    "UP": [pygame.K_w, pygame.K_UP],
    "DOWN": [pygame.K_s, pygame.K_DOWN],
    "RIGHT": [pygame.K_d, pygame.K_RIGHT],
    "LEFT": [pygame.K_a, pygame.K_LEFT],
    "FIRE": [pygame.K_SPACE],
    "START": [pygame.K_RETURN, pygame.K_SPACE],
    "ESC": [pygame.K_ESCAPE],
}
