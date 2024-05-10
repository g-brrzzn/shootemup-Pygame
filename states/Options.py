from states.GameState import GameState
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *


class Options(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(100)

    def start(self):
        self.selected = 0
        self.config_res = config.window_size

        
    def update(self, surf=screen):
        self.fall.update(-3, 0)
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        self.options = [f'RESOLUTION - {self.config_res}', f'SHOW FPS: {bool2Switch(config.show_fps)}',
                        f'FULLSCREEN: {bool2Switch(config.set_fullscreen)}', 'APPLY RESOLUTION', 'BACK']
        MenuMaker(self.options, __class__.__name__, self.selected, surf)

    def get_event(self, event):

        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
                if self.selected == len(self.options) - 1:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
                if self.selected == 0:
                    self.selected = len(self.options) - 1
                else:
                    self.selected -= 1

            if event.key in CONTROLS['RIGHT']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
                if self.selected == 0:
                    selec = config.RESOLUTIONS.index(self.config_res)
                    if selec == 0: self.config_res = config.RESOLUTIONS[0]
                    else: self.config_res = config.RESOLUTIONS[selec - 1]; selec -= 1

            if event.key in CONTROLS['LEFT']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
                if self.selected == 0:
                    selec = config.RESOLUTIONS.index(self.config_res)
                    if selec == len(config.RESOLUTIONS) - 1: self.config_res = config.RESOLUTIONS[len(config.RESOLUTIONS) - 1]
                    else: self.config_res = config.RESOLUTIONS[selec + 1]; selec += 1
            config.window_size = self.config_res
            if event.key in CONTROLS['START']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/forceField_001.mp3'))
                if self.selected == 0:
                    pass
                elif self.selected == 1:
                    print("\"Show FPS\" is not available in this version ")
                    config.show_fps = not config.show_fps
                elif self.selected == 2:
                    # SET_FULLSCREEN = not SET_FULLSCREEN
                    print("\"Set Fullscreen\" is not available in this version ")
                    config.set_fullscreen = not config.set_fullscreen
                elif self.selected == 3:
                    if config.window_size != (1280, 720):
                        print("Resolution config is not available in this version, please come back to the 720p")
                    if config.set_fullscreen:   screen = pygame.display.set_mode(config.window_size, pygame.FULLSCREEN)
                    else:                       screen = pygame.display.set_mode(config.window_size)
                elif self.selected == 4:
                    self.next_state = 'Menu'
                    self.done = True
            if event.key in CONTROLS['ESC']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
                self.next_state = 'Menu'
                self.done = True

    def draw(self, surf):
        self.fall.draw(surf, (200, 200, 200))

