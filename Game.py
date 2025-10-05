import pygame
from pygame.locals import *
import sys
from time import time

from classes.Bullet import Bullet
from classes.Enemy import EnemyBase, Enemy1, Enemy2, Enemy3
from classes.Player import Player
from classes.particles.Fall import Fall
from classes.particles.Explosion import Explosion
from assets.AssetManager import AssetManager

from states.Menu import Menu
from states.Pause import Pause
from states.GameState import GameState
from states.Options import Options
from states.GameOver import GameOver, Exit
from states.States_util import vertical, draw_text

from constants.global_var import SCALE, config, FRAME_RATE, BACKGROUND_COLOR_GAME_1, BACKGROUND_COLOR_GAME_2, CONTROLS
from constants.Utils import delta_time


pygame.init()
clock = pygame.time.Clock()
last_time = time()

if config.set_fullscreen:
    screen = pygame.display.set_mode(config.window_size, pygame.FULLSCREEN, vsync=True)
else:
    screen = pygame.display.set_mode(config.window_size, vsync=True)
game_surface = pygame.Surface(config.INTERNAL_RESOLUTION)
    
assets = AssetManager()
assets.load_assets(SCALE)
Bullet.load_assets(assets)
EnemyBase.load_assets(assets)

pygame.mixer.init()
pygame.mixer.music.load(assets.get_sound('music'))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

class Game(GameState):
    level = 1
    def __init__(self): 
        super().__init__()
        
        self.all_sprites = pygame.sprite.Group()
        self.all_enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        self.player = Player((config.INTERNAL_RESOLUTION[0] / 2, (config.INTERNAL_RESOLUTION[1] / 2)+150), assets, self.all_sprites)
        self.explosion = Explosion()
        self.background_fall = Fall(300)
        self.particles = pygame.sprite.Group()
        
        self.next_state = "Pause"
        self.last_time = last_time
        self.level = 1
        self.level_done = False

    def start(self):
        if self.player.getLife() <= 0:
            self.player.kill() 
            for enemy in self.all_enemies:
                enemy.kill()
            self.level = 1
            self.player = Player((config.INTERNAL_RESOLUTION[0] / 2, (config.INTERNAL_RESOLUTION[1] / 2)+150), assets, self.all_sprites)
            self.next_state = "Pause"

        if not self.level_done:         
            EnemyBase.spawn_enemy(self.level * 5, Enemy1, assets, self.all_enemies, self.all_sprites)
            self.level_done = False

    def get_event(self, event, assets):
        if event.type == KEYDOWN:
            self.player.get_input(event)

            if event.key in CONTROLS['ESC']:
                self.done = True
        if event.type == KEYUP:
            self.player.get_input_keyup(event)

    def update(self, assets):
        dt, self.last_time = delta_time(self.last_time)
    
        self.player.update(dt, assets, self.player_bullets, self.all_sprites)
        self.all_enemies.update(dt, self.player, assets, self.enemy_bullets, self.all_sprites)
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)
        self.background_fall.update(gravity=self.level*3/3)
        self.explosion.update(dt)
        self.particles.update(dt)

        enemy_hits = pygame.sprite.groupcollide(self.all_enemies, self.player_bullets, False, True)
        for enemy in enemy_hits:
            self.explosion.create(enemy.rect.centerx, enemy.rect.centery)
            enemy.damage()

        player_hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if player_hits:
            self.player.take_damage(assets)
            
        player_crashes = pygame.sprite.spritecollide(self.player, self.all_enemies, False)
        if player_crashes:
            self.player.take_damage(assets)
            for enemy in player_crashes:
                enemy.kill() 

        if not self.all_enemies:
            self.level += 1
            EnemyBase.spawn_enemy(self.level * 5, Enemy1, assets, self.all_enemies, self.all_sprites)
            EnemyBase.spawn_enemy(self.level * 2, Enemy2, assets, self.all_enemies, self.all_sprites)
            EnemyBase.spawn_enemy(self.level * 1, Enemy3, assets, self.all_enemies, self.all_sprites)
            self.level_done = True
            
        if self.player.getLife() <= 0:
            self.next_state = "GameOver"
            self.done = True

    def draw(self, surf, assets):
        vertical(surf, False, BACKGROUND_COLOR_GAME_1, BACKGROUND_COLOR_GAME_2)
        self.background_fall.draw(surf)
        
        self.all_sprites.draw(surf)
        
        self.player.explosion.draw(surf)
        self.explosion.draw(surf)
        for enemy in self.all_enemies:
            enemy.explosion.draw(surf)
            
        draw_text(surf, f'Level {self.level}', config.INTERNAL_RESOLUTION[0] - 50, config.INTERNAL_RESOLUTION[1] - 30, assets, use_smaller_font=False)
        draw_text(surf, f'Life    {self.player.getLife()}', config.INTERNAL_RESOLUTION[0] - 50, config.INTERNAL_RESOLUTION[1] - 60, assets, use_smaller_font=False)
        if config.show_fps:
            draw_text(surf, f'FPS {(int(clock.get_fps()))}', 50, 30, assets, use_smaller_font=False)


class GameRunner(object):
    def __init__(self, screen, game_surface, states, start_state):
        self.screen = screen
        self.game_surface = game_surface
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
        self.state.draw(self.game_surface, assets)
        scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.update()
        clock.tick(FRAME_RATE)


if __name__ == "__main__":
    states = {
        "Menu":     Menu(),
        "Game":     Game(),
        "Pause":    Pause(),
        "Exit":     Exit(),
        "Options":  Options(),
        "GameOver": GameOver()
    }
    game = GameRunner(screen, game_surface, states, "Menu")

