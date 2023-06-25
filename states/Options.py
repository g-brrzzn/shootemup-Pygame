from states.GameState import GameState
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *
from Classes import Fall

global SHOW_FPS
global SET_FULLSCREEN
global WINDOW_SIZE

class Options(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(100)

    def start(self):
        self.selected = 0
        self.config_res = WINDOW_SIZE

        
    def update(self, surf=screen):
        self.fall.update(-3, 0)
        vertical(surf, False, (60, 5, 40, 20), (25, 2, 10, 20))
        self.options = [f'RESOLUTION - {self.config_res}', f'SHOW FPS: {bool2Switch(SHOW_FPS)}',
                        f'FULLSCREEN: {bool2Switch(SET_FULLSCREEN)}', 'APPLY RESOLUTION', 'BACK']
        MenuMaker(self.options, __class__.__name__, self.selected, surf)

    def get_event(self, event):

        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                if self.selected == len(self.options) - 1:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                if self.selected == 0:
                    self.selected = len(self.options) - 1
                else:
                    self.selected -= 1

            if event.key in CONTROLS['RIGHT']:
                if self.selected == 0:
                    selec = ALL_RES.index(self.config_res)
                    if selec == 0: self.config_res = ALL_RES[0]
                    else: self.config_res = ALL_RES[selec - 1]; selec -= 1

            if event.key in CONTROLS['LEFT']:
                if self.selected == 0:
                    selec = ALL_RES.index(self.config_res)
                    if selec == len(ALL_RES) - 1: self.config_res = ALL_RES[len(ALL_RES) - 1]
                    else: self.config_res = ALL_RES[selec + 1]; selec += 1
            WINDOW_SIZE = self.config_res
            if event.key in CONTROLS['START']:
                if self.selected == 0:
                    pass
                elif self.selected == 1:
                    # SHOW_FPS = not SHOW_FPS
                    print("\"Show FPS\" is not available in this version ")
                elif self.selected == 2:
                    # SET_FULLSCREEN = not SET_FULLSCREEN
                    print("\"Set Fullscreen\" is not available in this version ")
                elif self.selected == 3:
                    if WINDOW_SIZE != (1280, 720):
                        print("Resolution config is not available in this version, please come back to the 720p")
                    if SET_FULLSCREEN: screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
                    else: screen = pygame.display.set_mode(WINDOW_SIZE)
                elif self.selected == 4:
                    self.next_state = 'Menu'
                    self.done = True
            if event.key in CONTROLS['ESC']:
                self.next_state = 'Menu'
                self.done = True

    def draw(self, surf):
        self.fall.draw(surf, (200, 200, 200))

