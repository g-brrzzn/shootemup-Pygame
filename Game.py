import pygame
from pygame.locals import *
import sys
from time import time
import random

from game_engine import g_engine
from classes.Bullet import Bullet
from classes.Enemy import EnemyBase, Enemy1, Enemy2, Enemy3
from classes.Boss import Boss
from classes.Player import Player
from classes.particles.Fall import Fall
from classes.particles.Explosion import Explosion
from classes.particles.Spark import Spark
from classes.EnemyFormations import FormationManager
from assets.AssetManager import AssetManager

from states.Menu import Menu
from states.Pause import Pause
from states.GameState import GameState
from states.Options import Options
from states.GameOver import GameOver, Exit
from states.States_util import vertical, draw_text

from constants.global_var import (
    SCALE,
    config,
    FRAME_RATE,
    BACKGROUND_COLOR_GAME_1,
    BACKGROUND_COLOR_GAME_2,
    CONTROLS,
)

from constants.Utils import delta_time, get_high_score, save_high_score
from constants.ShaderManager import ShaderManager

pygame.init()
clock = pygame.time.Clock()
last_time = time()

display_flags = pygame.DOUBLEBUF
if config.set_fullscreen:
    display_flags |= pygame.FULLSCREEN

if config.use_opengl:
    display_flags |= pygame.OPENGL
    screen = pygame.display.set_mode(config.window_size, display_flags, vsync=True)
    shader_manager = ShaderManager(config.INTERNAL_RESOLUTION, screen.get_size())
    game_surface = shader_manager.get_draw_surface()
    g_engine.shader_manager = shader_manager
else:
    screen = pygame.display.set_mode(config.window_size, display_flags, vsync=True)
    shader_manager = None
    g_engine.shader_manager = None
    game_surface = pygame.Surface(config.INTERNAL_RESOLUTION, pygame.SRCALPHA)

g_engine.assets = AssetManager()
g_engine.assets.load_assets(SCALE)
Bullet.load_assets(g_engine.assets)
EnemyBase.load_assets(g_engine.assets)

pygame.mixer.init()
pygame.mixer.music.load(g_engine.assets.get_sound("music"))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)


class Game(GameState):
    def __init__(self):
        super().__init__()

        g_engine.all_sprites = pygame.sprite.Group()
        g_engine.all_enemies = pygame.sprite.Group()
        g_engine.player_bullets = pygame.sprite.Group()
        g_engine.enemy_bullets = pygame.sprite.Group()
        g_engine.powerups = pygame.sprite.Group()

        g_engine.player = Player(
            (
                config.INTERNAL_RESOLUTION[0] / 2,
                (config.INTERNAL_RESOLUTION[1] / 2) + 150,
            ),
            g_engine.all_sprites,
        )
        self.explosion = Explosion()
        self.background_fall = Fall(300)
        self.stars_back = Fall(
            amount=150, min_s=0.1, max_s=0.2, color=(150, 150, 150), size=1, alpha=200
        )
        self.stars_mid = Fall(
            amount=60, min_s=0.5, max_s=1.0, color=(180, 180, 200), size=2, alpha=150
        )
        self.stars_front = Fall(
            amount=20, min_s=4.0, max_s=6.0, color=(200, 220, 255), size=4, alpha=60
        )
        self.particles = pygame.sprite.Group()
        g_engine.sparks = []

        self.next_state = "Pause"
        self.last_time = time()
        g_engine.level = 1
        self.level_done = False
        self.boss_active = False

        self.formations_to_spawn = 0
        self.current_wave_delay = 0
        self.wave_timer = 0

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
        self.spawn_next_formation()
        self.wave_timer = 0

    def spawn_next_formation(self):
        if self.formations_to_spawn > 0:
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
                self.done = True
        if event.type == KEYUP:
            g_engine.player.get_input_keyup(event)
        if event.type == JOYBUTTONDOWN:
            g_engine.player.get_controller_input(event)
            if event.button == 7:
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
        if dt > 3.0:
            dt = 3.0

        if g_engine.hit_stop_frames > 0:
            g_engine.hit_stop_frames -= 1
            self.explosion.update(dt)
            for spk in g_engine.sparks:
                spk.update(dt)
            return

        g_engine.all_sprites.update(dt)
        base_speed = g_engine.level * 0.5

        self.stars_back.update(gravity=base_speed * 0.1, dt=dt)
        self.stars_mid.update(gravity=base_speed * 0.5, dt=dt)
        self.stars_front.update(gravity=base_speed * 1.5, dt=dt)
        self.explosion.update(dt)
        self.particles.update(dt)

        for bullet in g_engine.enemy_bullets:
            if not getattr(bullet, "grazed", False):
                dist = pygame.math.Vector2(bullet.rect.center).distance_to(
                    g_engine.player.rect.center
                )
                if dist < 45:
                    bullet.grazed = True
                    g_engine.score += 50
                    spk = Spark(
                        bullet.rect.center,
                        random.randint(0, 360),
                        random.randint(3, 7),
                        (100, 200, 255),
                        scale=1.2,
                    )
                    g_engine.sparks.append(spk)

        enemy_hits = pygame.sprite.groupcollide(
            g_engine.all_enemies, g_engine.player_bullets, False, True
        )
        for enemy in enemy_hits:
            if isinstance(enemy, Boss):
                self.explosion.create(
                    enemy.rect.centerx, enemy.rect.centery + random.randint(-20, 20)
                )
                enemy.damage()
                g_engine.hit_stop_frames = 2
            else:
                self.explosion.create(enemy.rect.centerx, enemy.rect.centery)
                enemy.damage()

            for _ in range(random.randint(4, 8)):
                spk = Spark(
                    enemy.rect.center,
                    random.randint(0, 360),
                    random.randint(3, 10),
                    (255, 255, 180),
                    scale=1.5,
                )
                g_engine.sparks.append(spk)

        player_hits = pygame.sprite.spritecollide(
            g_engine.player, g_engine.enemy_bullets, True
        )
        if player_hits:
            g_engine.player.take_damage()
            g_engine.hit_stop_frames = 5
            if config.apply_controller_vibration and g_engine.joystick:
                g_engine.joystick.rumble(50, 200, 100)

        powerup_hits = pygame.sprite.spritecollide(
            g_engine.player, g_engine.powerups, True
        )
        for powerup in powerup_hits:
            if powerup.p_type == "weapon":
                g_engine.player.upgrade()
            elif powerup.p_type == "life":
                g_engine.player.gain_life()
            pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))

        for spk in g_engine.sparks[:]:
            spk.update(dt)
            if spk.life <= 0:
                g_engine.sparks.remove(spk)

        player_crashes = pygame.sprite.spritecollide(
            g_engine.player, g_engine.all_enemies, False
        )
        if player_crashes:
            g_engine.player.take_damage()
            g_engine.hit_stop_frames = 5
            if config.apply_controller_vibration and g_engine.joystick:
                g_engine.joystick.rumble(50, 200, 100)
            for enemy in player_crashes:
                g_engine.screen_shake = max(g_engine.screen_shake, 5)
                if not isinstance(enemy, Boss):
                    enemy.kill()

        if self.formations_to_spawn > 0:
            is_clear = len(g_engine.all_enemies) == 0
            if self.current_wave_delay > 0:
                self.current_wave_delay -= dt

            if self.current_wave_delay <= 0 or (
                is_clear and self.current_wave_delay < 100
            ):
                self.spawn_next_formation()

        elif len(g_engine.all_enemies) == 0:
            if self.boss_active:
                self.boss_active = False
                g_engine.level += 1
                self.start_next_level_waves()
            else:
                if g_engine.level % 3 == 0:
                    self.boss_active = True
                    Boss(
                        (config.INTERNAL_RESOLUTION[0] / 2, -100),
                        g_engine.all_enemies,
                        g_engine.all_sprites,
                    )
                else:
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

        g_engine.player.draw_particles(surf)
        g_engine.player.draw_muzzle_flash(surf)

        for bullet in g_engine.player_bullets:
            glow_rect = bullet.glow_image.get_rect(center=bullet.rect.center)
            surf.blit(bullet.glow_image, glow_rect, special_flags=pygame.BLEND_ADD)

        for bullet in g_engine.enemy_bullets:
            glow_rect = bullet.glow_image.get_rect(center=bullet.rect.center)
            surf.blit(bullet.glow_image, glow_rect, special_flags=pygame.BLEND_ADD)

        g_engine.all_sprites.draw(surf)

        for enemy in g_engine.all_enemies:
            if isinstance(enemy, Boss):
                enemy.draw(surf)

        for spk in g_engine.sparks:
            spk.draw(surf)

        self.explosion.draw(surf)
        for enemy in g_engine.all_enemies:
            enemy.explosion.draw(surf)

        self.stars_front.draw(surf)

        draw_text(
            surf,
            f"Score {g_engine.score:06d}",
            config.INTERNAL_RESOLUTION[0] / 2,
            30,
            use_smaller_font=False,
        )
        draw_text(
            surf,
            f"Level {g_engine.level}",
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
        pygame.display.set_icon(g_engine.assets.get_image("icon"))
        pygame.display.set_caption(
            f"Shoot 'em Up - Pygame. FPS: {int(clock.get_fps())}"
        )

        if not self.shader_manager:
            self.game_surface.fill((0, 0, 0, 0))

        self.state.draw(self.game_surface)

        render_offset = [0, 0]
        if g_engine.screen_shake > 0:
            g_engine.screen_shake -= 1
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
        clock.tick(FRAME_RATE)


if __name__ == "__main__":
    g_engine.high_score = get_high_score()
    states = {
        "Menu": Menu(),
        "Game": Game(),
        "Pause": Pause(),
        "Exit": Exit(),
        "Options": Options(),
        "GameOver": GameOver(),
    }

    start_state = "Menu"
    if "--options" in sys.argv:
        start_state = "Options"

    game = GameRunner(screen, shader_manager, game_surface, states, start_state)
