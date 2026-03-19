import sys
import pygame
from pygame.locals import *

from game_engine import g_engine
from .GameState import GameState
from .States_util import vertical, menu_maker
from classes.particles.Fall import Fall
from constants.global_var import CONTROLS, GAME_COLOR


class Exit(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Pause"

    def start(self):
        self.selected = 0

    def update(self):
        pass

    def draw(self, surf):
        menu_maker(
            ["EXIT TO MAIN-MENU", "EXIT TO DESKTOP", "BACK"],
            __class__.__name__,
            self.selected,
            surf,
            False,
        )

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["DOWN"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                if self.selected == 2:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS["UP"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                if self.selected == 0:
                    self.selected = 2
                else:
                    self.selected -= 1
            if event.key in CONTROLS["START"]:
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
            if event.key in CONTROLS["ESC"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.next_state = "Pause"
                self.done = True

        if event.type == JOYHATMOTION:
            if event.hat == 0:
                x, y = event.value

                if y == -1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    if self.selected == 2:
                        self.selected = 0
                    else:
                        self.selected += 1
                elif y == 1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    if self.selected == 0:
                        self.selected = 2
                    else:
                        self.selected -= 1

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

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
            print("Joystick added")
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None
            print("Joystick removed")


class GameOver(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Game"

    def start(self):
        self.selected = 0
        self.fall = Fall(amount=50, min_s=0.1, max_s=0.3, color=GAME_COLOR, size=4)

    def update(self):
        self.fall.update(-2, 3)

    def draw(self, surf):
        vertical(surf)
        self.fall.draw(surf)
        menu_maker(["RESTART", "EXIT"], __class__.__name__, self.selected, surf, False)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["DOWN"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                if self.selected == 1:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS["UP"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                if self.selected == 0:
                    self.selected = 1
                else:
                    self.selected -= 1
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
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    if self.selected == 1:
                        self.selected = 0
                    else:
                        self.selected += 1
                elif y == 1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    if self.selected == 0:
                        self.selected = 1
                    else:
                        self.selected -= 1

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    self.next_state = "Menu"
                    self.done = True
                elif self.selected == 1:
                    self.next_state = "Exit"
                    self.done = True

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None
