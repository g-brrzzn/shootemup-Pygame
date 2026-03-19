import pygame
from time import time
from pygame.locals import *
from random import randint, choice

from game_engine import g_engine
from classes.Bullet import Bullet
from classes.particles.Explosion import Explosion
from constants.global_var import (
    MAX_LIFE,
    CONTROLS,
    config,
    SPRITE_SIZE,
    PLAYER_COLOR_GREEN,
    GAME_COLOR,
)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.shot_delay = 0.25
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.firing = False
        self.last_time = time()
        self.last_shot = self.last_time

        self.original_sprites = [
            g_engine.assets.get_image("player_idle1"),
            g_engine.assets.get_image("player_idle2"),
        ]

        self.original_white_sprites = [
            self.create_white_surface(s) for s in self.original_sprites
        ]

        self.current_sprite_index = 0

        self.image = self.original_sprites[self.current_sprite_index]
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=pos)

        self.movement = pygame.math.Vector2()
        self.speed = config.INTERNAL_RESOLUTION[1] * 0.007

        self.life = MAX_LIFE
        self.explosion = Explosion()

        self.last_hit = 0
        self.invincibility_duration = 100
        self.power_level = 1

        self.angle = 0
        self.target_angle = 0
        self.exhaust_particles = []
        self.muzzle_flashes = []
        self.trail = []

    def create_white_surface(self, surface):
        mask = pygame.mask.from_surface(surface)
        white_surface = mask.to_surface(
            setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)
        )
        white_surface.set_colorkey((0, 0, 0))
        return white_surface

    def get_input(self, event):
        if event.key in CONTROLS["LEFT"]:
            self.moving_left = True
        if event.key in CONTROLS["RIGHT"]:
            self.moving_right = True
        if event.key in CONTROLS["DOWN"]:
            self.moving_down = True
        if event.key in CONTROLS["UP"]:
            self.moving_up = True
        if event.key in CONTROLS["FIRE"]:
            self.firing = True

        if event.key == K_o:
            if self.shot_delay >= 0.1:
                self.shot_delay -= 0.1
        if event.key == K_l:
            if self.shot_delay < 0.25:
                self.shot_delay += 0.1
        if event.key == K_i:
            self.speed += 1
        if event.key == K_k:
            if self.speed >= 7:
                self.speed -= 1

    def get_input_keyup(self, event):
        if event.key in CONTROLS["LEFT"]:
            self.moving_left = False
        if event.key in CONTROLS["RIGHT"]:
            self.moving_right = False
        if event.key in CONTROLS["DOWN"]:
            self.moving_down = False
        if event.key in CONTROLS["UP"]:
            self.moving_up = False
        if event.key in CONTROLS["FIRE"]:
            self.firing = False

    def get_controller_input(self, event):
        if event.button == 0:  # a button on xbox
            if self.shot_delay >= 0.1:
                self.shot_delay -= 0.1
        if event.button == 1:  # b button on xbox
            if self.shot_delay < 0.25:
                self.shot_delay += 0.1
        if event.button == 5:  # right bumper
            self.speed += 1
        if event.button == 4:  # left bumper
            if self.speed >= 7:
                self.speed -= 1

    def get_joyhat_input(self, event):
        if event.hat == 0:
            x, y = event.value

        if x == -1:
            self.moving_left = True
        elif x == 1:
            self.moving_right = True
        else:
            self.moving_left = False
            self.moving_right = False
        if y == -1:
            self.moving_down = True
        elif y == 1:
            self.moving_up = True
        else:
            self.moving_down = False
            self.moving_up = False

    def get_joyaxismotion_input(self, event):
        if event.axis == 5:
            if event.value > 0.5:
                self.firing = True
            else:
                self.firing = False

    def fire(self):
        for _ in range(2):
            self.muzzle_flashes.append([randint(-2, 2), randint(2, 6), randint(3, 5)])

        options = {"angle": 90}
        pattern = "single"

        if self.power_level == 2:
            pattern = "spread"
            options["count"] = 2
            options["spread_arc"] = 15
        elif self.power_level >= 3:
            pattern = "spread"
            options["count"] = 3
            options["spread_arc"] = 30

        Bullet.create_bullets(
            pattern=pattern,
            pos=self.rect.center,
            is_from_player=True,
            groups=(g_engine.player_bullets, g_engine.all_sprites),
            options=options,
        )
        pygame.mixer.Sound.play(g_engine.assets.get_sound("shoot"))
        if config.apply_controller_vibration and g_engine.joystick:
            g_engine.joystick.rumble(5, 50, 20)

    def upgrade(self):
        self.power_level = min(self.power_level + 1, 3)
        self.shot_delay = max(0.1, self.shot_delay - 0.02)

    def update_particles(self):
        offset_x = randint(-12, 12)
        p_x = self.rect.centerx + offset_x
        p_y = self.rect.bottom - 20

        color = choice([(167, 94, 67), (198, 128, 127)])
        radius = randint(6, 10)

        if self.moving_up:
            radius += 4

        self.exhaust_particles.append([p_x, p_y, radius, color, 255])

        for p in self.exhaust_particles[:]:
            p[1] += 5
            p[2] -= 0.5
            p[4] -= 15

            if p[2] <= 0 or p[4] <= 0:
                try:
                    self.exhaust_particles.remove(p)
                except ValueError:
                    pass

        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 12:
            self.trail.pop(0)

    def update(self, dt):
        self.last_time = time()
        self.explosion.update(dt)
        self.update_particles()

        max_flash_radius = 25
        for flash in self.muzzle_flashes[:]:
            flash[1] += flash[2]
            if flash[1] > max_flash_radius:
                self.muzzle_flashes.remove(flash)

        self.current_sprite_index += 0.07
        if self.current_sprite_index >= len(self.original_sprites):
            self.current_sprite_index = 0

        if self.moving_right:
            self.rect.x += round(self.speed * dt)
        if self.moving_left:
            self.rect.x -= round(self.speed * dt)
        if self.moving_up:
            self.rect.y -= round(self.speed * dt)
        if self.moving_down:
            self.rect.y += round(self.speed * dt)

        if self.rect.right > config.INTERNAL_RESOLUTION[0]:
            self.rect.right = config.INTERNAL_RESOLUTION[0]
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > config.INTERNAL_RESOLUTION[1]:
            self.rect.bottom = config.INTERNAL_RESOLUTION[1]
        if self.rect.top < 0:
            self.rect.top = 0

        target_angle = 0
        if self.moving_left:
            target_angle = 10
        if self.moving_right:
            target_angle = -10

        self.angle += (target_angle - self.angle) * 0.1 * dt

        current_time = pygame.time.get_ticks()
        is_invincible = current_time - self.last_hit < self.invincibility_duration

        idx = int(self.current_sprite_index)
        if is_invincible and (current_time // 100) % 2 == 1:
            base_image = self.original_white_sprites[idx]
        else:
            base_image = self.original_sprites[idx]

        self.image = pygame.transform.rotate(base_image, self.angle)
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect(center=self.rect.center)

        if self.firing and self.last_time - self.last_shot > self.shot_delay:
            self.fire()
            self.last_shot = self.last_time

    def draw_particles(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            radius = int((i / len(self.trail)) * 9)
            if radius > 0:
                surf_trail = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                alpha = int((i / len(self.trail)) * 120)
                pygame.draw.circle(
                    surf_trail, (*PLAYER_COLOR_GREEN, alpha), (radius, radius), radius
                )
                surf.blit(surf_trail, (tx - radius, ty - radius))

        for p in self.exhaust_particles:
            x, y, r, c, a = p
            radius_int = int(r)
            if radius_int <= 0:
                continue

            particle_surf = pygame.Surface(
                (radius_int * 2, radius_int * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                particle_surf, (*c, int(a)), (radius_int, radius_int), radius_int
            )
            surf.blit(particle_surf, (x - radius_int, y - radius_int))

        self.explosion.draw(surf)

    def draw_muzzle_flash(self, surf):
        max_flash_radius = 25.0
        center_x = self.rect.centerx

        for flash in self.muzzle_flashes:
            offset_y, radius, speed = flash
            center_y = self.rect.top + offset_y

            alpha = int(255 * (1.0 - (radius / max_flash_radius)))
            if alpha <= 0:
                continue
            rad_int = int(radius)
            flash_surf = pygame.Surface((rad_int * 2, rad_int * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                flash_surf, (*GAME_COLOR, alpha), (rad_int, rad_int), rad_int, 3
            )
            surf.blit(flash_surf, (center_x - rad_int, center_y - rad_int))

    def take_damage(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit > self.invincibility_duration:
            self.life -= 1
            self.power_level = 1
            self.last_hit = current_time
            self.explosion.create(
                self.rect.center[0] - SPRITE_SIZE / 2,
                self.rect.center[1] - SPRITE_SIZE,
                PLAYER_COLOR_GREEN,
                speed=-5,
            )
            pygame.mixer.Sound.play(g_engine.assets.get_sound("hit"))
            g_engine.screen_shake = 15

    def getLife(self):
        return self.life

    def setLife(self, life):
        self.life = life

    def gain_life(self):
        self.life += 1

    def getPowerLevel(self):
        return self.power_level

    def setPowerLevel(self, power_level):
        self.power_level = power_level

    def getX(self):
        return self.rect.x

    def getY(self):
        return self.rect.y
