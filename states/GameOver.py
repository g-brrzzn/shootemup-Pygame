import sys
import pygame
from pygame.locals import *

from states.GameState import GameState
from constants.global_func import vertical, MenuMaker
from classes.particles.Fall import Fall
from constants.global_var import CONTROLS, GAME_COLOR

class Exit(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = 'Pause'
        

    def start(self):
        self.selected = 0

    def update(self, assets):
        pass
        
    def draw(self, surf, assets):
        MenuMaker(['EXIT TO MAIN-MENU', 'EXIT TO DESKTOP', 'BACK'], __class__.__name__, self.selected, surf, assets)

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
                    self.next_state = 'Menu'
                    self.done = True
                elif self.selected == 1:
                    pygame.quit()
                    sys.exit()
                elif self.selected == 2:
                    self.next_state = 'Pause'
                    self.done = True
            if event.key in CONTROLS['ESC']:
                pygame.mixer.Sound.play(assets.get_sound('menu_select'))
                self.next_state = 'Pause'
                self.done = True


class GameOver(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = 'Game' 

    def start(self):
        self.selected = 0
        self.fall = Fall(100)

    def update(self, assets):
        self.fall.update(-2, 3)
        
    def draw(self, surf, assets):
        vertical(surf)
        self.fall.draw(surf, GAME_COLOR)
        MenuMaker(['RESTART', 'EXIT'], __class__.__name__, self.selected, surf, assets)
        
    def get_event(self, event, assets):
        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                pygame.mixer.Sound.play(assets.get_sound('menu_select'))
                if self.selected == 1:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                pygame.mixer.Sound.play(assets.get_sound('menu_select'))
                if self.selected == 0:
                    self.selected = 1
                else:
                    self.selected -= 1
            if event.key in CONTROLS['START']:
                pygame.mixer.Sound.play(assets.get_sound('menu_confirm'))
                if self.selected == 0:
                    self.next_state = 'Menu'
                    self.done = True
                elif self.selected == 1:
                    self.next_state = 'Exit'
                    self.done = True

