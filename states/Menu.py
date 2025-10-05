import pygame
from pygame.locals import *
import sys
import math
from random import randint

from .GameState import GameState
from .States_util import title_text, vertical, menu_maker
from classes.particles.Fall import Fall
from constants.Utils import delta_time
from constants.global_var import config, CONTROLS, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2

class Menu(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(100)

    def start(self):
        self.selected = 0
        self.last_time = pygame.time.get_ticks()

    def update(self, assets):
        dt, self.last_time = delta_time(self.last_time)
        self.fall.update(-3, 0)
        self.title_pos_y_offset = config.INTERNAL_RESOLUTION[1] * 0.04 * math.sin(2 * math.pi * pygame.time.get_ticks()/1000)
             
    def draw(self, surf, assets):
        self.fall.draw(surf, (200, 200, 200))
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        title_text(surf, "Shoot'em Up - Pygame",  randint(1,5) + config.INTERNAL_RESOLUTION[0]/2, self.title_pos_y_offset + config.INTERNAL_RESOLUTION[1] / 2 - config.INTERNAL_RESOLUTION[1]*0.33, assets)
        menu_maker(['START', 'OPTIONS', 'EXIT'], __class__.__name__, self.selected, surf, assets)

    def get_event(self, event, assets):
        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                pygame.mixer.Sound.play(assets.get_sound('menu_select'))
                if self.selected == 2:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                pygame.mixer.Sound.play(assets.get_sound('menu_select'))
                if self.selected == 0:
                    self.selected = 2
                else:
                    self.selected -= 1
            if event.key in CONTROLS['START']:
                pygame.mixer.Sound.play(assets.get_sound('menu_confirm'))
                if self.selected == 0:
                    self.next_state = 'Game'
                    self.done = True
                elif self.selected == 1:
                    self.next_state = 'Options'
                    self.done = True
                elif self.selected == 2:
                    pygame.quit()
                    sys.exit()



