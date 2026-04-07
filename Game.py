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

from states.Menu import Menu
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
pygame.mixer.music.load(g_engine.assets.get_sound("music"))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)


class Game(GameState):
    def __init__(self, ai_stage="full"):
        super().__init__()

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
                options = ["LINE_HORIZONTAL"]
            elif self.ai_stage == "single_enemy":
                options = ["LINE_HORIZONTAL", "V_SHAPE"]
            elif self.ai_stage == "swarm":
                options = [
                    "V_SHAPE",
                    "LINE_HORIZONTAL",
                    "DIAGONAL_LEFT",
                    "DIAGONAL_RIGHT",
                    "CIRCLE_CLUSTER",
                    "RANDOM_RAIN",
                ]
            elif self.ai_stage == "boss":
                options = [
                    "V_SHAPE",
                    "DIAGONAL_LEFT",
                    "DIAGONAL_RIGHT",
                    "CIRCLE_CLUSTER",
                ]
            else:
                options = [
                    "V_SHAPE",
                    "LINE_HORIZONTAL",
                    "DIAGONAL_LEFT",
                    "DIAGONAL_RIGHT",
                    "CIRCLE_CLUSTER",
                    "RANDOM_RAIN",
                ]

            choice_idx = min(len(options), 2 + g_engine.level)
            ftype = random.choice(options[:choice_idx])

            FormationManager.spawn_formation(ftype, g_engine.level)
            self.formations_to_spawn -= 1
            self.current_wave_delay = 120
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
        if event.type == KEYUP:
            g_engine.player.get_input_keyup(event)
            
            
        # --- LEVEL UP BUTTON (DEBUG) ----------------
            if event.key == K_TAB:
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "LevelUp"
                self.done = True
        # --------------------------------------------    
            
            
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

        if g_engine.enemy_bullets.active_count > 0:
            p_rect = g_engine.player.hitbox
            n = g_engine.enemy_bullets.active_count
            b_x = g_engine.enemy_bullets.pos[:n, 0]
            b_y = g_engine.enemy_bullets.pos[:n, 1]

            not_grazed = ~g_engine.enemy_bullets.grazed[:n]
            grazes = np.nonzero(
                (b_x >= p_rect.left - 40)
                & (b_x <= p_rect.right + 40)
                & (b_y >= p_rect.top - 40)
                & (b_y <= p_rect.bottom + 40)
                & not_grazed
            )[0]

            for g in grazes:
                g_engine.enemy_bullets.grazed[g] = True
                g_engine.score += 10
                g_engine.spark_system.emit(
                    pos=(
                        g_engine.enemy_bullets.pos[g, 0],
                        g_engine.enemy_bullets.pos[g, 1],
                    ),
                    angle=random.randint(0, 360),
                    speed=random.randint(3, 7),
                    color=(100, 200, 255),
                    scale=1.2,
                )

            hits = np.nonzero(
                (b_x >= p_rect.left)
                & (b_x <= p_rect.right)
                & (b_y >= p_rect.top)
                & (b_y <= p_rect.bottom)
            )[0]

            if len(hits) > 0:
                for h in reversed(hits):
                    meta = g_engine.enemy_bullets.get_bullet_meta(h)
                    
                    p_rect = g_engine.player.hitbox
                    parry_rect = g_engine.player.parry_rect 
                    bullets_to_kill = set()

                    if g_engine.player.parry_active:
                        possible_parrys = np.nonzero(
                            (b_x >= parry_rect.left) & (b_x <= parry_rect.right) &
                            (b_y >= parry_rect.top) & (b_y <= parry_rect.bottom)
                        )[0]
                        
                        for h in possible_parrys:
                            meta = g_engine.enemy_bullets.get_bullet_meta(h)
                            if meta.get("is_pink") and h not in bullets_to_kill:
                                g_engine.score += 150
                                g_engine.player.gain_exp(1)
                                g_engine.player.on_parry_success()
                                bullets_to_kill.add(h)

                    hits = np.nonzero(
                        (b_x >= p_rect.left) & (b_x <= p_rect.right) &
                        (b_y >= p_rect.top) & (b_y <= p_rect.bottom)
                    )[0]

                    for h in hits:
                        if h in bullets_to_kill: 
                            continue 
                        
                        if g_engine.player.take_damage():
                            bullets_to_kill.add(h)
                            g_engine.hit_stop_frames = 0.08
                            if config.apply_controller_vibration and g_engine.joystick:
                                g_engine.joystick.rumble(50, 200, 100)

                    for h in sorted(list(bullets_to_kill), reverse=True):
                        g_engine.enemy_bullets.kill_bullet(h)

        if g_engine.player_bullets.active_count > 0 and len(g_engine.all_enemies) > 0:
            n = g_engine.player_bullets.active_count
            b_x = g_engine.player_bullets.pos[:n, 0]
            b_y = g_engine.player_bullets.pos[:n, 1]

            bullets_to_kill = set()

            for enemy in list(g_engine.all_enemies):
                ex, ey, ew, eh = (
                    enemy.rect.x,
                    enemy.rect.y,
                    enemy.rect.width,
                    enemy.rect.height,
                )
                hits = np.nonzero(
                    (b_x >= ex) & (b_x <= ex + ew) & (b_y >= ey) & (b_y <= ey + eh)
                )[0]

                valid_hits = [h for h in hits if h not in bullets_to_kill]

                if valid_hits:
                    for h in valid_hits:
                        bullets_to_kill.add(h)

                    if isinstance(enemy, Boss):
                        g_engine.explosion_system.create(
                            enemy.rect.centerx,
                            enemy.rect.centery + random.randint(-20, 20),
                        )
                        enemy.damage()
                    else:
                        g_engine.explosion_system.create(
                            enemy.rect.centerx, enemy.rect.centery
                        )
                        enemy.damage()

                    for _ in range(random.randint(4, 8)):
                        g_engine.spark_system.emit(
                            pos=enemy.rect.center,
                            angle=random.randint(0, 360),
                            speed=random.randint(3, 10),
                            color=(255, 255, 180),
                            scale=1.5,
                        )

            for h in sorted(list(bullets_to_kill), reverse=True):
                g_engine.player_bullets.kill_bullet(h)

        powerup_hits = pygame.sprite.spritecollide(
            g_engine.player,
            g_engine.powerups,
            True,
            collided=lambda p, pw: p.hitbox.colliderect(pw.hitbox),
        )
        for powerup in powerup_hits:
            if powerup.p_type == "weapon":
                g_engine.player.upgrade()
            elif powerup.p_type == "life":
                g_engine.player.gain_life()
            pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))

        g_engine.spark_system.update(dt)

        player_crashes = pygame.sprite.spritecollide(
            g_engine.player,
            g_engine.all_enemies,
            False,
            collided=lambda p, e: p.hitbox.colliderect(e.rect),
        )
        if player_crashes:
            if g_engine.player.take_damage():
                g_engine.hit_stop_frames = 0.08
                g_engine.screen_shake = max(g_engine.screen_shake, 0.1)
                if config.apply_controller_vibration and g_engine.joystick:
                    g_engine.joystick.rumble(50, 200, 100)
            
            for enemy in player_crashes:
                if not isinstance(enemy, Boss):
                    enemy.kill()

        if hasattr(self, 'total_formations_current_wave'):
            if len(g_engine.all_enemies) == 0:
                self.formations_beaten_in_wave = self.total_formations_current_wave - self.formations_to_spawn
            else:
                self.formations_beaten_in_wave = max(0, self.total_formations_current_wave - self.formations_to_spawn - 1)

        if self.formations_to_spawn > 0:
            is_clear = len(g_engine.all_enemies) == 0

            if self.current_wave_delay > 0:
                self.current_wave_delay -= dt

            if self.current_wave_delay <= 0 or (is_clear and self.current_wave_delay < 100000):
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

        if g_engine.player and g_engine.player.getLife() > 0:
            bar_width = config.INTERNAL_RESOLUTION[0] * 0.4 
            bar_height = 8
            x_pos = (config.INTERNAL_RESOLUTION[0] - bar_width) // 2
            
            if self.boss_active:
                boss = next((e for e in g_engine.all_enemies if isinstance(e, Boss)), None)
                fill_pct = max(0.0, boss.life / boss.max_life) if boss else 0.0
            else:
                total_forms = max(1, getattr(self, 'total_formations_current_wave', 1))
                beaten = getattr(self, 'formations_beaten_in_wave', 0)
                fill_pct = beaten / total_forms

            fill_width = int(fill_pct * bar_width)
            
            pygame.draw.rect(surf, (20, 30, 35), (x_pos, 15, bar_width, bar_height))
            pygame.draw.rect(surf, (0, 255, 150), (x_pos, 15, fill_width, bar_height))
            pygame.draw.rect(surf, (200, 200, 200), (x_pos, 15, bar_width, bar_height), 1)


        draw_text(
            surf,
            f"Score {g_engine.score:06d}",
            config.INTERNAL_RESOLUTION[0] / 2,
            45, 
            use_smaller_font=False,
        )
        draw_text(
            surf,
            f"Wave {g_engine.level}",
            config.INTERNAL_RESOLUTION[0] - 50,
            config.INTERNAL_RESOLUTION[1] - 30,
            use_smaller_font=False,
        )
        draw_text(
            surf,
            f"Life   {max(0, g_engine.player.getLife())}",
            config.INTERNAL_RESOLUTION[0] - 50,
            config.INTERNAL_RESOLUTION[1] - 60,
            use_smaller_font=False,
        )

        if config.show_fps:
            draw_text(
                surf, f"FPS {(int(clock.get_fps()))}", 50, 30, use_smaller_font=False
            )


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
    }

    start_state = "Menu"
    if "--options" in sys.argv:
        start_state = "Options"

    game = GameRunner(screen, shader_manager, game_surface, states, start_state)