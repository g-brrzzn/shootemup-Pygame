import pygame
from pygame.locals import *

from game_engine import g_engine
from .GameState import GameState
from .States_util import vertical, menu_maker, get_on_off_status
from classes.particles.Fall import Fall
from constants.global_var import config, CONTROLS, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2


class Options(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(100)

    def start(self):
        self.selected = 0
        self.config_res = config.window_size
        self.options = [f'RESOLUTION - {self.config_res}', f'SHOW FPS: {get_on_off_status(config.show_fps)}',
                        f'FULLSCREEN: {get_on_off_status(config.set_fullscreen)}', 'APPLY RESOLUTION', 'BACK']

        
    def update(self):
        self.fall.update(-3, 0) 
        self.options = [f'RESOLUTION - {self.config_res}', f'SHOW FPS: {get_on_off_status(config.show_fps)}',
                        f'FULLSCREEN: {get_on_off_status(config.set_fullscreen)}', 'APPLY RESOLUTION', 'BACK']
            
    def draw(self, surf):
        self.fall.draw(surf, (200, 200, 200))
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        menu_maker(self.options, __class__.__name__, self.selected, surf)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                pygame.mixer.Sound.play(g_engine.assets.get_sound('menu_select'))
                if self.selected == len(self.options) - 1:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                pygame.mixer.Sound.play(g_engine.assets.get_sound('menu_select'))
                if self.selected == 0:
                    self.selected = len(self.options) - 1
                else:
                    self.selected -= 1

            if event.key in CONTROLS['RIGHT']:
                pygame.mixer.Sound.play(g_engine.assets.get_sound('menu_select'))
                if self.selected == 0:
                    selec = config.RESOLUTIONS.index(self.config_res)
                    if selec == 0: self.config_res = config.RESOLUTIONS[0]
                    else: self.config_res = config.RESOLUTIONS[selec - 1]; selec -= 1

            if event.key in CONTROLS['LEFT']:
                pygame.mixer.Sound.play(g_engine.assets.get_sound('menu_select'))
                if self.selected == 0:
                    selec = config.RESOLUTIONS.index(self.config_res)
                    if selec == len(config.RESOLUTIONS) - 1: self.config_res = config.RESOLUTIONS[len(config.RESOLUTIONS) - 1]
                    else: self.config_res = config.RESOLUTIONS[selec + 1]; selec += 1
            config.window_size = self.config_res
            
            if event.key in CONTROLS['START']:
                pygame.mixer.Sound.play(g_engine.assets.get_sound('menu_confirm'))
                if self.selected == 0:
                    pass
                elif self.selected == 1:
                    config.show_fps = not config.show_fps
                elif self.selected == 2:                   
                    config.set_fullscreen = not config.set_fullscreen
                elif self.selected == 3:
                    if config.set_fullscreen:   screen = pygame.display.set_mode(config.window_size, pygame.FULLSCREEN)
                    else:                       screen = pygame.display.set_mode(config.window_size)
                elif self.selected == 4:
                    self.next_state = 'Menu'
                    self.done = True
            if event.key in CONTROLS['ESC']:
                pygame.mixer.Sound.play(g_engine.assets.get_sound('menu_select'))
                self.next_state = 'Menu'
                self.done = True