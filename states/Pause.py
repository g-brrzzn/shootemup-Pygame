from states.GameState import GameState
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *


class Exit(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = 'Pause'

    def start(self):
        self.selected = 0

    def update(self, surf=screen):
        MenuMaker(['EXIT TO MAIN-MENU', 'EXIT TO DESKTOP', 'BACK'], __class__.__name__, self.selected, surf)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                if self.selected == 2:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                if self.selected == 0:
                    self.selected = 2
                else:
                    self.selected -= 1
            if event.key in CONTROLS['START']:
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
                self.next_state = 'Pause'
                self.done = True


class Pause(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = 'Game'

    def start(self):
        self.selected = 0

    def update(self, surf=screen):
        MenuMaker(['CONTINUE', 'OPTIONS', 'EXIT'], __class__.__name__, self.selected, surf)

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                if self.selected == 2:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                if self.selected == 0:
                    self.selected = 2
                else:
                    self.selected -= 1
            if event.key in CONTROLS['START']:
                if self.selected == 0:
                    self.next_state = 'Game'
                    self.done = True
                elif self.selected == 1:
                    # self.next_state = 'GameOptions'
                    # self.done = True
                    print("Ingame Options not available in this version")
                elif self.selected == 2:
                    self.next_state = 'Exit'
                    self.done = True
            if event.key == K_ESCAPE:
                self.next_state = 'Game'
                self.done = True

