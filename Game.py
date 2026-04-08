import pygame
from pygame.locals import *
import sys
from time import time
import random
import numpy as np
from platform import system

from game_engine import g_engine
from classes.Bullet import BulletSystem
from classes.Enemy import EnemyBase, Enemy1, Enemy2, Enemy3
from classes.Boss import Boss
from classes.Player import Player
from classes.particles.Fall import Fall
from classes.particles.Explosion import ExplosionSystem
from classes.particles.Spark import SparkSystem
from classes.EnemyFormations import FormationManager
from assets.AssetManager import AssetManager
from classes.CollisionManager import CollisionManager
from classes.HUD import HUD

from states.Menu import Menu
from states.ModMenu import ModMenu
from states.Pause import Pause
from states.GameState import GameState
from states.Options import Options
from states.GameOver import GameOver, Exit
from states.LevelUp import LevelUp
from states.States_util import vertical, draw_text

from constants.global_var import (
    SCALE,
    config,
    BACKGROUND_COLOR_GAME_1,
    BACKGROUND_COLOR_GAME_2,
    CONTROLS,
)

from constants.Utils import delta_time, get_high_score, save_high_score
from constants.ShaderManager import ShaderManager

pygame.init()
clock = pygame.time.Clock()
last_time = time()

g_engine.platform = system()

display_flags = pygame.DOUBLEBUF
if config.set_fullscreen:
    display_flags |= pygame.FULLSCREEN

if config.use_opengl:
    display_flags |= pygame.OPENGL
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
    )
    screen = pygame.display.set_mode(config.window_size, display_flags, vsync=False)
    shader_manager = ShaderManager(config.INTERNAL_RESOLUTION, screen.get_size())
    game_surface = shader_manager.get_draw_surface()
    g_engine.shader_manager = shader_manager
else:
    screen = pygame.display.set_mode(config.window_size, display_flags, vsync=False)
    shader_manager = None
    g_engine.shader_manager = None
    game_surface = pygame.Surface(config.INTERNAL_RESOLUTION, pygame.SRCALPHA)

if g_engine.fps_limit is None:
    g_engine.fps_limit = pygame.display.get_current_refresh_rate()
    if g_engine.fps_limit not in config.FPS_LIMITS:
        g_engine.fps_limit = 75

g_engine.assets = AssetManager()
g_engine.assets.load_assets(SCALE)
pygame.display.set_icon(g_engine.assets.get_image("icon"))
BulletSystem.load_assets(g_engine.assets)
EnemyBase.load_assets(g_engine.assets)

pygame.mixer.init()

MUSIC_END_EVENT = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(MUSIC_END_EVENT)

def play_random_music():
    if g_engine.assets.music_tracks:      
        track = random.choice(g_engine.assets.music_tracks)
        pygame.mixer.music.load(track)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play() 

play_random_music()

class Game(GameState):
    def __init__(self, ai_stage="full"):
        super().__init__()
        
        self.hud = HUD()

        g_engine.all_sprites = pygame.sprite.Group()
        g_engine.all_enemies = pygame.sprite.Group()
        g_engine.powerups = pygame.sprite.Group()

        g_engine.player_bullets = BulletSystem(max_particles=2000, is_player=True)
        g_engine.enemy_bullets = BulletSystem(max_particles=15000, is_player=False)
        
        g_engine.player_bullets.set_orbit_anchor_provider(lambda: g_engine.player.rect.center if g_engine.player else None)
        g_engine.player_bullets.set_target_provider(lambda: g_engine.all_enemies)

        g_engine.player = Player(
            (
                config.INTERNAL_RESOLUTION[0] / 2,
                (config.INTERNAL_RESOLUTION[1] / 2) + 150,
            ),
            g_engine.all_sprites,
        )
        self.background_fall = Fall(300)
        self.stars_back = Fall(
            amount=150, min_s=7.5, max_s=15.0, color=(150, 150, 150), size=1, alpha=200
        )
        self.stars_mid = Fall(
            amount=60, min_s=37.5, max_s=75, color=(180, 180, 200), size=2, alpha=150
        )
        self.stars_front = Fall(
            amount=20, min_s=300.0, max_s=450.0, color=(200, 220, 255), size=4, alpha=60
        )
        self.particles = pygame.sprite.Group()

        g_engine.spark_system = SparkSystem(max_particles=5000)
        g_engine.explosion_system = ExplosionSystem(max_particles=5000)

        self.next_state = "Pause"
        self.last_time = time()
        g_engine.level = 1
        self.level_done = False
        self.boss_active = False

        self.formations_to_spawn = 0
        self.total_formations_current_wave = 1
        self.formations_beaten_in_wave = 0
        self.current_wave_delay = 0
        self.wave_timer = 0
        self.ai_stage = ai_stage

        joysticks = [
            pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
        ]
        if joysticks:
            g_engine.joystick = joysticks[0]

    def start(self):
        self.last_time = time()

        if g_engine.player.getLife() <= 0:
            g_engine.player.kill()
            for enemy in g_engine.all_enemies:
                enemy.kill()
            for p in g_engine.powerups:
                p.kill()
            g_engine.player_bullets.active_count = 0
            g_engine.enemy_bullets.active_count = 0
            g_engine.level = 1
            g_engine.score = 0
            self.boss_active = False
            g_engine.player = Player(
                (
                    config.INTERNAL_RESOLUTION[0] / 2,
                    (config.INTERNAL_RESOLUTION[1] / 2) + 150,
                ),
                g_engine.all_sprites,
            )
            self.next_state = "Pause"

        if not self.boss_active and len(g_engine.all_enemies) == 0:
            self.start_next_level_waves()

    def start_next_level_waves(self):
        self.formations_to_spawn = 3 + (g_engine.level * 2)
        self.total_formations_current_wave = self.formations_to_spawn
        self.formations_beaten_in_wave = 0
        
        self.spawn_next_formation()
        self.wave_timer = 0

    def spawn_next_formation(self):
        if self.formations_to_spawn > 0:
            if self.ai_stage == "movement":
                options = ["LINE_HORIZONTAL", "BLOCKADE"]
            elif self.ai_stage == "single_enemy":
                options = ["LINE_HORIZONTAL", "V_SHAPE", "BLOCKADE"]
            elif self.ai_stage == "boss":
                options = [
                    "V_SHAPE",
                    "DIAGONAL_LEFT",
                    "DIAGONAL_RIGHT",
                    "CIRCLE_CLUSTER",
                    "PINCER",
                ]
            else:
                options = [
                    "V_SHAPE",
                    "LINE_HORIZONTAL",
                    "DIAGONAL_LEFT",
                    "DIAGONAL_RIGHT",
                    "CIRCLE_CLUSTER",
                    "RANDOM_RAIN",
                    "ENTER_AND_STOP",
                    "SWEEP_CROSS",
                    "PINCER",
                    "BLOCKADE",
                    "CROSSFIRE",
                ]

            choice_idx = min(len(options), 3 + g_engine.level)
            available_options = options[:choice_idx]

            is_combo = g_engine.level >= 2 and random.random() < 0.35 and self.formations_to_spawn > 1

            if is_combo:
                f1, f2 = random.sample(available_options, 2)
                FormationManager.spawn_formation(f1, g_engine.level)
                FormationManager.spawn_formation(f2, g_engine.level)
                self.formations_to_spawn -= 2
                self.current_wave_delay = random.uniform(3.5, 5.5)
            else:
                ftype = random.choice(available_options)
                FormationManager.spawn_formation(ftype, g_engine.level)
                self.formations_to_spawn -= 1
                self.current_wave_delay = random.uniform(2.5, 4.0)
        else:
            self.level_done = True

    def get_event(self, event):
        if event.type == KEYDOWN:
            g_engine.player.get_input(event)
            if event.key in CONTROLS["ESC"]:
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "Pause"
                self.done = True
                
            if event.key in CONTROLS.get("MOD_MENU", [K_BACKSPACE]):
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "ModMenu"
                self.done = True
                
        if event.type == KEYUP:
            g_engine.player.get_input_keyup(event)
            
            if event.key == K_TAB:
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "LevelUp"
                self.done = True
            
        if event.type == JOYBUTTONDOWN:
            g_engine.player.get_controller_input(event)
            if (
                event.button == 7
                or (event.button == 11 and g_engine.platform == "Linux")
                or (event.button == 6 and g_engine.platform == "Darwin")
            ):
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "Pause"
                self.done = True
                
            if event.button in [4, 6]:
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "ModMenu"
                self.done = True
                
        if event.type == JOYBUTTONUP:
            g_engine.player.get_controller_keyup(event)
            
        if event.type == JOYAXISMOTION:
            g_engine.player.get_joyaxismotion_input(event)
            
        if event.type == JOYHATMOTION:
            g_engine.player.get_joyhat_input(event)
            
        if event.type == JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            g_engine.joystick = joystick
            
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
        if dt > 0.1:
            dt = 0.1

        if g_engine.hit_stop_frames > 0:
            g_engine.hit_stop_frames -= dt
            g_engine.explosion_system.update(dt)
            g_engine.spark_system.update(dt)
            return

        g_engine.all_sprites.update(dt)
        g_engine.player_bullets.update(dt)
        g_engine.enemy_bullets.update(dt)

        base_speed = g_engine.level * 0.5
        self.stars_back.update(gravity=base_speed * 0.1, dt=dt)
        self.stars_mid.update(gravity=base_speed * 0.5, dt=dt)
        self.stars_front.update(gravity=base_speed * 1.5, dt=dt)

        g_engine.explosion_system.update(dt)
        self.particles.update(dt)
        g_engine.spark_system.update(dt)

        CollisionManager.update()

        if hasattr(self, 'total_formations_current_wave'):
            if len(g_engine.all_enemies) == 0:
                self.formations_beaten_in_wave = self.total_formations_current_wave - self.formations_to_spawn
            else:
                self.formations_beaten_in_wave = max(0, self.total_formations_current_wave - self.formations_to_spawn - 1)

        if self.formations_to_spawn > 0:
            is_clear = len(g_engine.all_enemies) == 0

            if self.current_wave_delay > 0:
                self.current_wave_delay -= dt

            if self.current_wave_delay <= 0 or is_clear:
                self.spawn_next_formation()

        elif len(g_engine.all_enemies) == 0:
            if self.boss_active:
                self.boss_active = False
                g_engine.level += 1
                self.start_next_level_waves()
            else:
                boss_every = 3
                if self.ai_stage == "movement": boss_every = 999999
                elif self.ai_stage == "single_enemy": boss_every = 999999
                elif self.ai_stage == "boss": boss_every = 2

                if g_engine.level % boss_every == 0:
                    self.boss_active = True
                    Boss(
                        (config.INTERNAL_RESOLUTION[0] / 2, -100),
                        g_engine.all_enemies,
                        g_engine.all_sprites,
                    )
                else:
                    if hasattr(g_engine.player, 'reset_movement'):
                        g_engine.player.reset_movement()
                    
                    self.next_state = "LevelUp"
                    self.done = True
                    
                    g_engine.level += 1
                    self.start_next_level_waves()

        if g_engine.player.getLife() <= 0:
            if g_engine.score > g_engine.high_score:
                g_engine.high_score = g_engine.score
                save_high_score(g_engine.high_score)

            self.next_state = "GameOver"
            self.done = True

    def draw(self, surf):
        vertical(surf, False, BACKGROUND_COLOR_GAME_1, BACKGROUND_COLOR_GAME_2)

        self.stars_back.draw(surf)
        self.stars_mid.draw(surf)

        player_glow = g_engine.assets.get_image("glow_player")
        surf.blit(
            player_glow,
            player_glow.get_rect(center=g_engine.player.rect.center),
            special_flags=pygame.BLEND_ADD,
        )
        
        g_engine.player.draw_absorb_effect(surf) 

        g_engine.player.draw_particles(surf)
        g_engine.player.draw_muzzle_flash(surf)

        g_engine.player_bullets.draw(surf)
        g_engine.enemy_bullets.draw(surf)

        g_engine.all_sprites.draw(surf)

        for enemy in g_engine.all_enemies:
            if isinstance(enemy, Boss):
                enemy.draw(surf)

        g_engine.spark_system.draw(surf)
        g_engine.explosion_system.draw(surf)

        self.stars_front.draw(surf)
        
        if getattr(g_engine, 'show_hitboxes', False):
            if g_engine.player and g_engine.player.getLife() > 0:
                pygame.draw.rect(surf, (0, 255, 0), g_engine.player.hitbox, 2)
                pygame.draw.rect(surf, (50, 150, 255), g_engine.player.parry_rect, 1)

            for enemy in g_engine.all_enemies:
                pygame.draw.rect(surf, (255, 50, 50), enemy.rect, 2)
                
            for pu in g_engine.powerups:
                pygame.draw.rect(surf, (255, 255, 0), pu.hitbox, 2)
                
            n_pb = g_engine.player_bullets.active_count
            for i in range(n_pb):
                px, py = g_engine.player_bullets.pos[i]
                pygame.draw.circle(surf, (0, 255, 100), (int(px), int(py)), 4, 1)
                
            n_eb = g_engine.enemy_bullets.active_count
            for i in range(n_eb):
                px, py = g_engine.enemy_bullets.pos[i]
                pygame.draw.circle(surf, (255, 100, 100), (int(px), int(py)), 4, 1)

        fill_pct = 0.0
        if self.boss_active:
            boss = next((e for e in g_engine.all_enemies if isinstance(e, Boss)), None)
            fill_pct = max(0.0, boss.life / boss.max_life) if boss else 0.0
        else:
            total_forms = max(1, getattr(self, 'total_formations_current_wave', 1))
            beaten = getattr(self, 'formations_beaten_in_wave', 0)
            fill_pct = beaten / total_forms

        self.hud.draw(surf, clock, fill_pct)


class GameRunner(object):
    def __init__(self, screen, shader_manager, game_surface, states, start_state):
        self.screen = screen
        self.shader_manager = shader_manager
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
            if event.type == MUSIC_END_EVENT:
                play_random_music()
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
        pygame.display.set_caption(
            f"Shoot 'em Up - Pygame. FPS: {int(clock.get_fps())}"
        )

        if not self.shader_manager:
            self.game_surface.fill((0, 0, 0, 0))

        self.state.draw(self.game_surface)

        render_offset = [0, 0]
        if g_engine.screen_shake > 0:
            g_engine.screen_shake -= clock.get_time() / 1000.0
            render_offset[0] = random.randint(-4, 4)
            render_offset[1] = random.randint(-4, 4)

        if self.shader_manager:
            self.shader_manager.draw(offset=render_offset)
        else:
            scaled_surface = pygame.transform.scale(
                self.game_surface, self.screen.get_size()
            )
            self.screen.blit(scaled_surface, render_offset)

        pygame.display.flip()
        clock.tick(g_engine.fps_limit)


if __name__ == "__main__":
    g_engine.high_score = get_high_score()
    states = {
        "Menu": Menu(),
        "Game": Game(),
        "Pause": Pause(),
        "Exit": Exit(),
        "Options": Options(),
        "GameOver": GameOver(),
        "LevelUp": LevelUp(), 
        "ModMenu": ModMenu(),
    }

    start_state = "Menu"
    if "--options" in sys.argv:
        start_state = "Options"

    game = GameRunner(screen, shader_manager, game_surface, states, start_state)