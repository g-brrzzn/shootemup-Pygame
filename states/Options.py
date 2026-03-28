import pygame
from time import time
from pygame.locals import *
import sys
import os
import subprocess

from game_engine import g_engine
from .GameState import GameState
from .States_util import (
    vertical,
    menu_maker,
    get_on_off_status,
    menu_select_next,
    menu_select_prev,
    handle_analog_stick,
)
from classes.particles.Fall import Fall
from constants.global_var import (
    config,
    CONTROLS,
    BACKGROUND_COLOR_MENU_1,
    BACKGROUND_COLOR_MENU_2,
)
from constants.Utils import delta_time


def restart_game(extra_args=None):
    extra_args = extra_args or []

    if getattr(sys, "frozen", False):
        # PyInstaller executable
        cmd = [sys.executable, *sys.argv[1:]]
    else:
        # Running with python
        cmd = [sys.executable, sys.argv[0], *sys.argv[1:]]

    for arg in extra_args:
        if arg not in cmd:
            cmd.append(arg)

    env = os.environ.copy()
    env.pop("_MEIPASS2", None)
    env.pop("_MEIPASS", None)

    subprocess.Popen(cmd, env=env)
    pygame.quit()
    raise SystemExit


class Options(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(amount=80, min_s=15, max_s=37.5, color=(200, 200, 200), size=2)

    def start(self):
        self.selected = 0
        self.config_res = config.window_size
        self.last_time = time()
        self.update_options_list()

    def update_options_list(self):
        self.options = [
            f"RESOLUTION - {self.config_res}",
            f"FPS LIMIT - {g_engine.fps_limit}",
            f"SHOW FPS: {get_on_off_status(config.show_fps)}",
            f"FULLSCREEN: {get_on_off_status(config.set_fullscreen)}",
            f"USE OPENGL: {get_on_off_status(config.use_opengl)}",
            f"VIBRATION: {get_on_off_status(config.apply_controller_vibration)}",
            f"ANALOG STICK: {get_on_off_status(config.use_analog_stick)}",
            "APPLY SETTINGS",
            "BACK",
        ]

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
        self.fall.update(-225, 0, dt)
        self.update_options_list()

    def draw(self, surf):
        self.fall.draw(surf)
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        menu_maker(self.options, __class__.__name__, self.selected, surf, True)

    def select_prev_res(self):
        pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
        if self.selected == 0:
            selected_res = config.RESOLUTIONS.index(self.config_res)
            selected_res = min(len(config.RESOLUTIONS) - 1, selected_res + 1)
            self.config_res = config.RESOLUTIONS[selected_res]
        config.window_size = self.config_res

    def select_next_res(self):
        pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
        if self.selected == 0:
            selected_res = config.RESOLUTIONS.index(self.config_res)
            selected_res = max(0, selected_res - 1)
            self.config_res = config.RESOLUTIONS[selected_res]
        config.window_size = self.config_res

    def select_prev_fps_limit(self):
        pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
        if self.selected == 1:
            selected_fps_limit = config.FPS_LIMITS.index(g_engine.fps_limit)
            selected_fps_limit = min(len(config.FPS_LIMITS) - 1, selected_fps_limit + 1)
            g_engine.fps_limit = config.FPS_LIMITS[selected_fps_limit]

    def select_next_fps_limit(self):
        pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
        if self.selected == 1:
            selected_fps_limit = config.FPS_LIMITS.index(g_engine.fps_limit)
            selected_fps_limit = max(0, selected_fps_limit - 1)
            g_engine.fps_limit = config.FPS_LIMITS[selected_fps_limit]

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["DOWN"]:
                menu_select_next(self, self.options)
            if event.key in CONTROLS["UP"]:
                menu_select_prev(self, self.options)

            if event.key in CONTROLS["RIGHT"]:
                if self.selected == 0:
                    self.select_next_res()
                elif self.selected == 1:
                    self.select_next_fps_limit()

            if event.key in CONTROLS["LEFT"]:
                if self.selected == 0:
                    self.select_prev_res()
                else:
                    self.select_prev_fps_limit()

            if event.key in CONTROLS["START"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected in (0, 1):
                    pass
                elif self.selected == 2:
                    config.show_fps = not config.show_fps
                elif self.selected == 3:
                    config.set_fullscreen = not config.set_fullscreen
                elif self.selected == 4:
                    config.use_opengl = not config.use_opengl
                elif self.selected == 5:
                    config.apply_controller_vibration = (
                        not config.apply_controller_vibration
                    )
                elif self.selected == 6:
                    config.use_analog_stick = not config.use_analog_stick
                elif self.selected == 7:
                    config.save()
                    restart_game(["--options"])
                elif self.selected == 8:
                    self.next_state = "Menu"
                    self.done = True

            if event.key in CONTROLS["ESC"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.next_state = "Menu"
                self.done = True

        if event.type == JOYHATMOTION:
            if event.hat == 0:
                x, y = event.value

                if y == -1:
                    menu_select_next(self, self.options)
                elif y == 1:
                    menu_select_prev(self, self.options)

                if x == 1:
                    if self.selected == 0:
                        self.select_next_res()
                    elif self.selected == 1:
                        self.select_next_fps_limit()
                elif x == -1:
                    if self.selected == 0:
                        self.select_prev_res()
                    else:
                        self.select_prev_fps_limit()

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected in (0, 1):
                    pass
                elif self.selected == 2:
                    config.show_fps = not config.show_fps
                elif self.selected == 3:
                    config.set_fullscreen = not config.set_fullscreen
                elif self.selected == 4:
                    config.use_opengl = not config.use_opengl
                elif self.selected == 5:
                    config.apply_controller_vibration = (
                        not config.apply_controller_vibration
                    )
                elif self.selected == 6:
                    config.use_analog_stick = not config.use_analog_stick
                elif self.selected == 7:
                    config.save()
                    restart_game(["--options"])
                elif self.selected == 8:
                    self.next_state = "Menu"
                    self.done = True

            if event.button == 1:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.next_state = "Menu"
                self.done = True

            if g_engine.platform == "Darwin":
                if event.button == 11:
                    menu_select_prev(self, self.options)
                if event.button == 12:
                    menu_select_next(self, self.options)

                if event.button == 13:
                    if self.selected == 0:
                        self.select_prev_res()
                    elif self.selected == 1:
                        self.select_prev_fps_limit()
                if event.button == 14:
                    if self.selected == 0:
                        self.select_next_res()
                    else:
                        self.select_next_fps_limit()

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick

        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None

        if event.type == JOYAXISMOTION and config.use_analog_stick:
            handle_analog_stick(self, event)
