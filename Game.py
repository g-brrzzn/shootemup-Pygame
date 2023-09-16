from Classes import *
from states.Menu import Menu
from states.Pause import *
from states.GameState import GameState
from states.Options import Options
from states.DeathScreen import *
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *

pygame.init()
clock = pygame.time.Clock()
if SET_FULLSCREEN: screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
else: screen = pygame.display.set_mode(WINDOW_SIZE)

last_time = time()


class Game(GameState):
    level = 1
    def __init__(self, screen=screen):
        super().__init__()
        self.player = Player((WINDOW_SIZE[0] / 2, (WINDOW_SIZE[1] / 2)+150))
        self.background_fall = Fall(300)
        self.bullets = Bullet(self.player.rect[0] + SPRITE_SIZE, self.player.rect[1] + SPRITE_SIZE / 2, 5)
        self.next_state = "Pause"
        self.last_time = last_time
        self.level = 1
        self.level_done = False

    def start(self):
        if not self.level_done:
            Enemy1.spawn_enemy(self.level * 5)
            self.level_done = True

    def get_event(self, event):
        if event.type == KEYDOWN:
            self.player.get_input(event)

            if event.key in CONTROLS['ESC']:
                self.done = True
        if event.type == KEYUP:
            self.player.get_input_keyup(event)

    def update(self, surf=screen):
        if SHOW_FPS: text(FRAME_RATE, 30, 30)
        dt, self.last_time = delta_time(self.last_time)
        self.bullets.update(dt, surf)
        self.player.update(dt, self.last_time)
        self.background_fall.update()
        if Enemy1.instancelist is not None: [instance.update(dt, surf) for instance in Enemy1.instancelist]
        if not len(Enemy1.instancelist):
            self.level += 1
            Enemy1.spawn_enemy(self.level * 5)
            self.level_done = True

    def draw(self, surf=screen):
        if SHOW_FPS:
            text(f'FPS: {(int(clock.get_fps()))}', 50, 30, original_font=False)
        text(f'Level {self.level}', WINDOW_SIZE[0]-50, WINDOW_SIZE[1]-30, original_font=False)

        vertical(surf, False, BACKGROUND_COLOR_GAME_1, BACKGROUND_COLOR_GAME_2)
        self.background_fall.draw(surf)
        self.player.draw(surf)


class GameRunner(object):
    def __init__(self, screen, states, start_state):
        self.screen = screen
        self.states = states
        self.start_state = start_state
        self.state = self.states[self.start_state]

        self.state.start()
        self.run()

    def run(self):
        running = True
        while running:
            self.get_events()
            self.update()
            self.draw()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            self.state.get_event(event)

    def update(self):
        self.state.update()
        if self.state.done:
            self.next_state()

    def next_state(self):
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        self.state = self.states[self.state_name]
        self.state.start()

    def quit(self):
        pygame.quit()
        sys.exit()

    def draw(self):

        pygame.display.set_icon(pygame.image.load('assets/player_idle1.png'))
        pygame.display.set_caption(f'Shoot \'em Up - Pygame. FPS: {int(clock.get_fps())}')
        clock.tick(FRAME_RATE)
        pygame.display.update()
        self.state.draw(self.screen)


if __name__ == "__main__":
    states = {
        "Menu":     Menu(),
        "Game":     Game(),
        "Pause":    Pause(),
        "Exit":     Exit(),
        "Options":  Options(),
        "Death":    Death()
    }
    game = GameRunner(screen, states, "Menu")

