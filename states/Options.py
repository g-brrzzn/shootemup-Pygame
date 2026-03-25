import pygame
from pygame.locals import *
import sys
import os

from game_engine import g_engine
from .GameState import GameState
from .States_util import (
    vertical,
    menu_maker,
    get_on_off_status,
    menu_select_next,
    menu_select_prev,
    select_next_res,
    select_prev_res,
    handle_analog_stick,
)
from classes.particles.Fall import Fall
from constants.global_var import (
    config,
    CONTROLS,
    BACKGROUND_COLOR_MENU_1,
    BACKGROUND_COLOR_MENU_2,
)


class Options(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(amount=80, min_s=0.2, max_s=0.5, color=(200, 200, 200), size=2)

    def start(self):
        self.selected = 0
        self.config_res = config.window_size
        self.update_options_list()

    def update_options_list(self):
        self.options = [
            f"RESOLUTION - {self.config_res}",
            f"SHOW FPS: {get_on_off_status(config.show_fps)}",
            f"FULLSCREEN: {get_on_off_status(config.set_fullscreen)}",
            f"USE OPENGL: {get_on_off_status(config.use_opengl)}",
            f"VIBRATION: {get_on_off_status(config.apply_controller_vibration)}",
            f"ANALOG STICK: {get_on_off_status(config.use_analog_stick)}",
            "APPLY SETTINGS",
            "BACK",
        ]

    def update(self):
        self.fall.update(-3, 0)
        self.update_options_list()

    def draw(self, surf):
        self.fall.draw(surf)
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        menu_maker(self.options, __class__.__name__, self.selected, surf, True)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["DOWN"]:
                menu_select_next(self, self.options)
            if event.key in CONTROLS["UP"]:
                menu_select_prev(self, self.options)

            if event.key in CONTROLS["RIGHT"]:
                select_next_res(self)

            if event.key in CONTROLS["LEFT"]:
                select_prev_res(self)

            if event.key in CONTROLS["START"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    pass
                elif self.selected == 1:
                    config.show_fps = not config.show_fps
                elif self.selected == 2:
                    config.set_fullscreen = not config.set_fullscreen
                elif self.selected == 3:
                    config.use_opengl = not config.use_opengl
                elif self.selected == 4:
                    config.apply_controller_vibration = (
                        not config.apply_controller_vibration
                    )
                elif self.selected == 5:
                    config.use_analog_stick = not config.use_analog_stick
                elif self.selected == 6:
                    config.save()
                    args = sys.argv.copy()
                    if "--options" not in args:
                        args.append("--options")
                    os.execl(sys.executable, sys.executable, *args)
                elif self.selected == 7:
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
                    select_next_res(self)

                elif x == -1:
                    select_prev_res(self)

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    pass
                elif self.selected == 1:
                    config.show_fps = not config.show_fps
                elif self.selected == 2:
                    config.set_fullscreen = not config.set_fullscreen
                elif self.selected == 3:
                    config.use_opengl = not config.use_opengl
                elif self.selected == 4:
                    config.apply_controller_vibration = (
                        not config.apply_controller_vibration
                    )
                elif self.selected == 5:
                    config.use_analog_stick = not config.use_analog_stick
                elif self.selected == 6:
                    config.save()
                    args = sys.argv.copy()
                    if "--options" not in args:
                        args.append("--options")
                    os.execl(sys.executable, sys.executable, *args)
                elif self.selected == 7:
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
                    select_prev_res(self)
                if event.button == 14:
                    select_next_res(self)

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None

        if event.type == JOYAXISMOTION and config.use_analog_stick:
            handle_analog_stick(self, event)
