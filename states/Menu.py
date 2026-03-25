import pygame
from pygame.locals import *
import sys
import math
from random import randint

from game_engine import g_engine
from .GameState import GameState
from .States_util import title_text, vertical, menu_maker, draw_text
from classes.particles.Fall import Fall
from constants.Utils import delta_time
from constants.global_var import (
    config,
    CONTROLS,
    BACKGROUND_COLOR_MENU_1,
    BACKGROUND_COLOR_MENU_2,
    TITLE_YELLOW_1,
)


class Menu(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(
            amount=120, min_s=0.2, max_s=0.5, color=(200, 200, 200), size=3
        )
        self.buttons = ["START", "OPTIONS", "EXIT"]

    def start(self):
        self.selected = 0
        self.last_time = pygame.time.get_ticks()
        self.title_pos_y_offset = 0

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
        self.fall.update(-3, 0)
        self.title_pos_y_offset = (
            config.INTERNAL_RESOLUTION[1]
            * 0.04
            * math.sin(2 * math.pi * pygame.time.get_ticks() / 1000)
        )

    def draw(self, surf):
        self.fall.draw(surf)
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        title_text(
            surf,
            "Shoot'em Up - Pygame",
            randint(1, 5) + config.INTERNAL_RESOLUTION[0] / 2,
            self.title_pos_y_offset
            + config.INTERNAL_RESOLUTION[1] / 2
            - config.INTERNAL_RESOLUTION[1] * 0.33,
        )
        hs_y_pos = (
            self.title_pos_y_offset
            + config.INTERNAL_RESOLUTION[1] / 2
            - config.INTERNAL_RESOLUTION[1] * 0.33
        ) + 60
        if g_engine.high_score > 0:
            draw_text(
                surf,
                f"HIGH SCORE: {g_engine.high_score:07d}",
                config.INTERNAL_RESOLUTION[0] / 2,
                hs_y_pos,
                TITLE_YELLOW_1,
            )
        menu_maker(self.buttons, __class__.__name__, self.selected, surf, False)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["DOWN"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.selected = (self.selected + 1) % len(self.buttons)
            if event.key in CONTROLS["UP"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.selected = (self.selected - 1) % len(self.buttons)
            if event.key in CONTROLS["START"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    self.next_state = "Game"
                    self.done = True
                elif self.selected == 1:
                    self.next_state = "Options"
                    self.done = True
                elif self.selected == 2:
                    pygame.quit()
                    sys.exit()

        if event.type == JOYHATMOTION:
            if event.hat == 0:
                x, y = event.value

                if y == -1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = (self.selected + 1) % len(self.buttons)
                elif y == 1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = (self.selected - 1) % len(self.buttons)

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                if self.selected == 0:
                    self.next_state = "Game"
                    self.done = True
                elif self.selected == 1:
                    self.next_state = "Options"
                    self.done = True
                elif self.selected == 2:
                    pygame.quit()
                    sys.exit()

            if g_engine.platform == "Darwin":
                if event.button == 11:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = (self.selected - 1) % len(self.buttons)
                if event.button == 12:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = (self.selected + 1) % len(self.buttons)

        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None

        if event.type == JOYAXISMOTION and config.use_analog_stick:
            deadzone = 0.5

            if event.axis == 1:
                if event.value > deadzone and not getattr(self, "axis_down", False):
                    self.axis_down = True
                    pygame.event.post(
                        pygame.event.Event(JOYHATMOTION, hat=0, value=(0, -1))
                    )
                elif event.value < -deadzone and not getattr(self, "axis_up", False):
                    self.axis_up = True
                    pygame.event.post(
                        pygame.event.Event(JOYHATMOTION, hat=0, value=(0, 1))
                    )
                elif abs(event.value) < deadzone:
                    self.axis_down = False
                    self.axis_up = False

            if event.axis == 0:
                if event.value > deadzone and not getattr(self, "axis_right", False):
                    self.axis_right = True
                    pygame.event.post(
                        pygame.event.Event(JOYHATMOTION, hat=0, value=(1, 0))
                    )
                elif event.value < -deadzone and not getattr(self, "axis_left", False):
                    self.axis_left = True
                    pygame.event.post(
                        pygame.event.Event(JOYHATMOTION, hat=0, value=(-1, 0))
                    )
                elif abs(event.value) < deadzone:
                    self.axis_right = False
                    self.axis_left = False
