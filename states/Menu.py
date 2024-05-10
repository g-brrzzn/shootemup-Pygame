from states.GameState import GameState
from constants.global_func import *
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import Fall


pygame.init()
screen = pygame.display.set_mode(config.window_size)


class Menu(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(100)

    def start(self):
        self.selected = 0

    def update(self, surf=screen):
        self.fall.update(-3, 0)
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)
        MenuMaker(['START', 'OPTIONS', 'EXIT'], __class__.__name__, self.selected, surf)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
                if self.selected == 2:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
                if self.selected == 0:
                    self.selected = 2
                else:
                    self.selected -= 1
            if event.key in CONTROLS['START']:
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/forceField_001.mp3'))
                if self.selected == 0:
                    self.next_state = 'Game'
                    self.done = True
                elif self.selected == 1:
                    self.next_state = 'Options'
                    self.done = True
                elif self.selected == 2:
                    pygame.quit()
                    sys.exit()

    def draw(self, surf):
        self.fall.draw(surf, (200, 200, 200))

