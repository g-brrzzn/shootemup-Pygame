import pygame
from pygame.locals import *
import sys
import math
from random import randint

from states.GameState import GameState
from constants.global_func import delta_time, title_text, vertical, MenuMaker, Fall
from constants.global_var import config, CONTROLS, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2


pygame.init()
screen = pygame.display.set_mode(config.window_size)


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
        title_text("Shoot\'em Up - Pygame", randint(1,5)+config.window_size[0]/2, 20*math.sin(2 * math.pi * pygame.time.get_ticks()/1000)+config.window_size[1] / 2 - 400, assets)
             
    def draw(self, surf, assets):
        self.fall.draw(surf, (200, 200, 200))
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        MenuMaker(['START', 'OPTIONS', 'EXIT'], __class__.__name__, self.selected, surf, assets)

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



