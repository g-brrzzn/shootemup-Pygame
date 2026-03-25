import pygame
from pygame.locals import *

from game_engine import g_engine
from .GameState import GameState
from .States_util import (
    menu_maker,
    menu_select_next,
    menu_select_prev,
    handle_analog_stick,
)
from constants.global_var import CONTROLS, config


class Pause(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Game"
        self.buttons = ["CONTINUE", "EXIT"]

    def start(self):
        self.selected = 0

    def update(self):
        pass

    def draw(self, surf):
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
                    menu_select_next(self, self.buttons)
                elif y == 1:
                    menu_select_prev(self, self.buttons)

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
