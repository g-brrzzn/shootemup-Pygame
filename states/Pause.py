import pygame
from pygame.locals import *

from game_engine import g_engine
from .GameState import GameState
from .States_util import menu_maker
from constants.global_var import CONTROLS


class Pause(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Game"

    def start(self):
        self.selected = 0

    def update(self):
        pass

    def draw(self, surf):
        menu_maker(["CONTINUE", "EXIT"], __class__.__name__, self.selected, surf)

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
                    self.next_state = "Game"
                    self.done = True
                elif self.selected == 1:
                    self.next_state = "Exit"
                    self.done = True
            if event.key == K_ESCAPE:
                self.next_state = "Game"
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
                    self.next_state = "Game"
                    self.done = True
                elif self.selected == 1:
                    self.next_state = "Exit"
                    self.done = True
            if event.button == 1:
                self.next_state = "Game"
                self.done = True

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None
