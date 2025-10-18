import pygame
from pygame.locals import *
import sys
from time import time
import random

from game_engine import g_engine
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
    
g_engine.assets = AssetManager()
g_engine.assets.load_assets(SCALE)
Bullet.load_assets(g_engine.assets)
EnemyBase.load_assets(g_engine.assets)

pygame.mixer.init()
pygame.mixer.music.load(g_engine.assets.get_sound('music'))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

class Game(GameState):
    def __init__(self): 
        super().__init__()
        
        g_engine.all_sprites = pygame.sprite.Group()
        g_engine.all_enemies = pygame.sprite.Group()
        g_engine.player_bullets = pygame.sprite.Group()
        g_engine.enemy_bullets = pygame.sprite.Group()
        
        g_engine.player = Player((config.INTERNAL_RESOLUTION[0] / 2, (config.INTERNAL_RESOLUTION[1] / 2)+150), g_engine.all_sprites)
        self.explosion = Explosion()
        self.background_fall = Fall(300)
        self.particles = pygame.sprite.Group()
        
        self.next_state = "Pause"
        self.last_time = last_time
        g_engine.level = 1
        self.level_done = False

    def start(self):
        if g_engine.player.getLife() <= 0:
            g_engine.player.kill() 
            for enemy in g_engine.all_enemies:
                enemy.kill()
            g_engine.level = 1
            g_engine.player = Player((config.INTERNAL_RESOLUTION[0] / 2, (config.INTERNAL_RESOLUTION[1] / 2)+150), g_engine.all_sprites)
            self.next_state = "Pause"

        if not self.level_done:     
            EnemyBase.spawn_enemy(g_engine.level * 5, Enemy1)
            self.level_done = False

    def get_event(self, event):
        if event.type == KEYDOWN:
            g_engine.player.get_input(event)
            if event.key in CONTROLS['ESC']:
                self.done = True
        if event.type == KEYUP:
            g_engine.player.get_input_keyup(event)

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
    
        g_engine.all_sprites.update(dt)
        self.background_fall.update(gravity=g_engine.level*3/3)
        self.explosion.update(dt)
        self.particles.update(dt)

        enemy_hits = pygame.sprite.groupcollide(g_engine.all_enemies, g_engine.player_bullets, False, True)
        for enemy in enemy_hits:
            self.explosion.create(enemy.rect.centerx, enemy.rect.centery)
            enemy.damage()

        player_hits = pygame.sprite.spritecollide(g_engine.player, g_engine.enemy_bullets, True)
        if player_hits:
            g_engine.player.take_damage()
            
        player_crashes = pygame.sprite.spritecollide(g_engine.player, g_engine.all_enemies, False)
        if player_crashes:
            g_engine.player.take_damage()
            for enemy in player_crashes:
                g_engine.screen_shake = max(g_engine.screen_shake, 5)
                enemy.kill() 

        if not g_engine.all_enemies:
            g_engine.level += 1
            EnemyBase.spawn_enemy(g_engine.level * 5, Enemy1)
            EnemyBase.spawn_enemy(g_engine.level * 2, Enemy2)
            EnemyBase.spawn_enemy(g_engine.level * 1, Enemy3)
            self.level_done = True
            
        if g_engine.player.getLife() <= 0:
            self.next_state = "GameOver"
            self.done = True

    def draw(self, surf):
        vertical(surf, False, BACKGROUND_COLOR_GAME_1, BACKGROUND_COLOR_GAME_2)
        self.background_fall.draw(surf)
        g_engine.all_sprites.draw(surf)
        g_engine.player.explosion.draw(surf)
        self.explosion.draw(surf)
        for enemy in g_engine.all_enemies:
            enemy.explosion.draw(surf)
            
        draw_text(surf, f'Level {g_engine.level}', config.INTERNAL_RESOLUTION[0] - 50, config.INTERNAL_RESOLUTION[1] - 30, use_smaller_font=False)
        draw_text(surf, f'Life   {g_engine.player.getLife()}', config.INTERNAL_RESOLUTION[0] - 50, config.INTERNAL_RESOLUTION[1] - 60, use_smaller_font=False)
        if config.show_fps:
            draw_text(surf, f'FPS {(int(clock.get_fps()))}', 50, 30, use_smaller_font=False)


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
        pygame.display.set_icon(g_engine.assets.get_image('icon'))
        pygame.display.set_caption(f'Shoot \'em Up - Pygame. FPS: {int(clock.get_fps())}')
        
        self.state.draw(self.game_surface)
        
        render_offset = [0, 0]
        if g_engine.screen_shake > 0:
            g_engine.screen_shake -= 1
            render_offset[0] = random.randint(-4, 4)
            render_offset[1] = random.randint(-4, 4)
            
        scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
        self.screen.blit(scaled_surface, render_offset)
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