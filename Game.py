from classes.Bullet import Bullet
from classes.Enemy import *
from classes.Player import Player
from assets.AssetManager import AssetManager

from states.Menu import Menu
from states.Pause import *
from states.GameState import GameState
from states.Options import Options
from states.GameOver import *
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *


pygame.init()
assets = AssetManager()
assets.load_assets(SCALE)
Bullet.load_assets(assets)
EnemyBase.load_assets(assets)

clock = pygame.time.Clock()
if config.set_fullscreen:   screen = pygame.display.set_mode(config.window_size, pygame.FULLSCREEN, vsync=True)
else:                       screen = pygame.display.set_mode(config.window_size, vsync=True)

last_time = time()
pygame.mixer.init()
pygame.mixer.music.load(assets.get_sound('music'))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)


class Game(GameState):
    level = 1
    def __init__(self, screen=screen):
        super().__init__()
        self.player = Player((config.window_size[0] / 2, (config.window_size[1] / 2)+150), assets)
        self.background_fall = Fall(300)
        self.bullets = Bullet(self.player.rect[0] + SPRITE_SIZE, self.player.rect[1] + SPRITE_SIZE / 2, 5)
        
        self.next_state = "Pause"
        self.last_time = last_time
        self.level = 1
        self.level_done = False

    def start(self):
        if Player.getLife(self.player) <= 0:
            del self.player
            [instance.kill() for instance in Enemy1.instancelist]
            [instance.kill() for instance in Enemy2.instancelist]
            [instance.kill() for instance in Enemy3.instancelist]
            self.level = 1
            self.player = Player((config.window_size[0] / 2, (config.window_size[1] / 2)+150), assets)
            self.next_state = "Pause"
        if not self.level_done:
            [instance.kill() for instance in Enemy1.instancelist]
            [instance.kill() for instance in Enemy2.instancelist]
            [instance.kill() for instance in Enemy3.instancelist]
            EnemyBase.spawn_enemy(self.level * 5, Enemy1, assets)
            self.level_done = False

    def get_event(self, event, assets):
        if event.type == KEYDOWN:
            self.player.get_input(event)

            if event.key in CONTROLS['ESC']:
                self.done = True
        if event.type == KEYUP:
            self.player.get_input_keyup(event)

    def update(self, surf=screen):
        dt, self.last_time = delta_time(self.last_time)
        
        self.bullets.update(dt)
        self.player.update(dt, self.last_time)
        self.background_fall.update(gravity=self.level*3/3)
        if Enemy1.instancelist is not None:
            [instance.update(dt, self.player, assets) for instance in Enemy1.instancelist]
        
        if not len(Enemy1.instancelist) and not len(Enemy2.instancelist) and not len(Enemy3.instancelist):
            self.level += 1
            EnemyBase.spawn_enemy(self.level * 5, Enemy1, assets)
            EnemyBase.spawn_enemy(self.level * 2, Enemy2, assets)
            EnemyBase.spawn_enemy(self.level * 1, Enemy3, assets)
            self.level_done = True
        if self.player.getLife() <= 0:
            self.next_state = "GameOver"
            self.done = True

    def draw(self, surf, assets):
        vertical(surf, False, BACKGROUND_COLOR_GAME_1, BACKGROUND_COLOR_GAME_2)
        self.background_fall.draw(surf)
        self.player.draw(surf, assets) 
        self.bullets.draw_all(surf)
        
        if Enemy1.instancelist is not None:
            for instance in Enemy1.instancelist:
                instance.draw(surf)
        if Enemy2.instancelist is not None:
            for instance in Enemy2.instancelist:
                instance.draw(surf)        
        if Enemy3.instancelist is not None:
            for instance in Enemy3.instancelist:
                instance.draw(surf)
        
        text(f'Level {self.level}', config.window_size[0] - 50, config.window_size[1] - 30, assets, original_font=False)
        text(f'Life    {self.player.getLife()}', config.window_size[0] - 50, config.window_size[1] - 60, assets, original_font=False)
        if config.show_fps:
            text(f'FPS {(int(clock.get_fps()))}', 50, 30, assets, original_font=False)


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

            self.state.get_event(event, assets)

    def update(self):
        self.state.update(assets)
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
        pygame.display.set_icon(pygame.image.load('assets/sprites/player/player_idle1.png'))
        pygame.display.set_caption(f'Shoot \'em Up - Pygame. FPS: {int(clock.get_fps())}')
        clock.tick(FRAME_RATE)
        pygame.display.update()
        self.state.draw(self.screen, assets)


if __name__ == "__main__":
    states = {
        "Menu":     Menu(),
        "Game":     Game(),
        "Pause":    Pause(),
        "Exit":     Exit(),
        "Options":  Options(),
        "GameOver": GameOver()
    }
    game = GameRunner(screen, states, "Menu")

