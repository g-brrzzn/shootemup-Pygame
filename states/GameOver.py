import sys
import pygame
from time import time
from pygame.locals import *

from game_engine import g_engine
from .GameState import GameState
from .States_util import (
    vertical,
    menu_maker,
    menu_select_next,
    menu_select_prev,
    handle_analog_stick,
)
from classes.particles.Fall import Fall
from constants.global_var import CONTROLS, GAME_COLOR, config
from constants.Utils import delta_time, save_high_score


class Exit(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Pause"
        self.buttons = ["EXIT TO MAIN-MENU", "EXIT TO DESKTOP", "BACK"]

    def start(self):
        self.selected = 0

    def update(self):
        pass

    def draw(self, surf):
        menu_maker(
            self.buttons,
            __class__.__name__,
            self.selected,
            surf,
            False,
        )
        
    def force_game_reset(self):
        if g_engine.score > g_engine.high_score:
            g_engine.high_score = g_engine.score
            save_high_score(g_engine.high_score)
        
        if g_engine.player:
            g_engine.player.setLife(0)
            
        self.next_state = "Menu"
        self.done = True

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["DOWN"]:
                menu_select_next(self, self.buttons)
            if event.key in CONTROLS["UP"]:
                menu_select_prev(self, self.buttons)
            if event.key in CONTROLS["START"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    self.force_game_reset()
                    self.done = True
                elif self.selected == 1:
                    pygame.quit()
                    sys.exit()
                elif self.selected == 2:
                    self.next_state = "Pause"
                    self.done = True
            if event.key in CONTROLS["ESC"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.next_state = "Pause"
                self.done = True

        if event.type == JOYHATMOTION:
            if event.hat == 0:
                x, y = event.value

                if y == -1:
                    menu_select_next(self, self.buttons)
                elif y == 1:
                    menu_select_prev(self, self.buttons)

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    self.next_state = "Menu"
                    self.done = True
                elif self.selected == 1:
                    pygame.quit()
                    sys.exit()
                elif self.selected == 2:
                    self.next_state = "Pause"
                    self.done = True
            if event.button == 1:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.next_state = "Pause"
                self.done = True

            if g_engine.platform == "Darwin":
                if event.button == 11:
                    menu_select_prev(self, self.buttons)
                if event.button == 12:
                    menu_select_next(self, self.buttons)

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None

        if event.type == JOYAXISMOTION and config.use_analog_stick:
            handle_analog_stick(self, event)


class GameOver(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Game"
        self.buttons = ["RESTART", "EXIT"]

    def start(self):
        self.selected = 0
        self.last_time = time()
        self.fall = Fall(amount=50, min_s=7.5, max_s=22.5, color=GAME_COLOR, size=4)

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
        self.fall.update(-150, 225, dt)

    def draw(self, surf):
        vertical(surf)
        self.fall.draw(surf)
        menu_maker(self.buttons, __class__.__name__, self.selected, surf, False)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["DOWN"]:
                menu_select_next(self, self.buttons)
            if event.key in CONTROLS["UP"]:
                menu_select_prev(self, self.buttons)
            if event.key in CONTROLS["START"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    self.next_state = "Menu"
                    self.done = True
                elif self.selected == 1:
                    self.next_state = "Exit"
                    self.done = True

        if event.type == JOYHATMOTION:
            if event.hat == 0:
                x, y = event.value

                if y == -1:
                    menu_select_next(self, self.buttons)
                elif y == 1:
                    menu_select_prev(self, self.buttons)

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    self.foce_game_reset()
                    self.done = True
                elif self.selected == 1:
                    self.next_state = "Exit"
                    self.done = True

            if g_engine.platform == "Darwin":
                if event.button == 11:
                    menu_select_prev(self, self.buttons)
                if event.button == 12:
                    menu_select_next(self, self.buttons)

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None

        if event.type == JOYAXISMOTION and config.use_analog_stick:
            handle_analog_stick(self, event)
