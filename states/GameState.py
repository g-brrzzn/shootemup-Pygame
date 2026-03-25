class GameState(object):

    def __init__(self):
        self.done = False
        self.axis_up = False
        self.axis_down = False
        self.axis_left = False
        self.axis_right = False

    def start(self):
        pass

    def update(self):
        pass

    def draw(self, surf, assets):
        pass

    def get_event(self, event):
        pass
