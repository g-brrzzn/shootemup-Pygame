from states.GameState import GameState
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *
from Classes import Fall

class Exit(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = 'Pause'
        self.fall = Fall(100)

    def start(self):
        self.selected = 0

    def update(self, surf=screen):
        MenuMaker(['EXIT TO MAIN-MENU', 'EXIT TO DESKTOP', 'BACK'], __class__.__name__, self.selected, surf)
        self.fall.update()

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


class Death(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = 'Game'
        self.fall = Fall(100)

    def start(self):
        self.selected = 0

    def update(self, surf=screen):
        MenuMaker(['RESTART', 'EXIT'], __class__.__name__, self.selected, surf)
        self.fall.update()

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS['DOWN']:
                if self.selected == 1:
                    self.selected = 0
                else:
                    self.selected += 1
            if event.key in CONTROLS['UP']:
                if self.selected == 0:
                    self.selected = 1
                else:
                    self.selected -= 1
            if event.key in CONTROLS['START']:
                if self.selected == 0:
                    self.next_state = 'Menu'
                    self.done = True
                elif self.selected == 1:
                    self.next_state = 'Exit'
                    self.done = True

