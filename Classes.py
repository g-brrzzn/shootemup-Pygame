import pygame.image

from constants.global_var import *
from constants.global_imports import *

pygame.init()
pygame.display.set_mode(WINDOW_SIZE)


class Fall:
    def __init__(self, quantidade):
        self.locs = []
        for i in range(quantidade):
            snowloc = [randint(1, WINDOW_SIZE[0] - 1), randint(1, WINDOW_SIZE[1] - 1)]
            self.locs.append(snowloc)

    def update(self, gravity=0.3, wind=0.3):
        for loc in self.locs:
            loc[1] += gravity + uniform(0.1, 0.9)

            if wind > 0:
                loc[0] += wind
            if gravity < 0:
                if loc[1] < 0: loc[1] = WINDOW_SIZE[1]
                if loc[0] < 0: loc[0] = WINDOW_SIZE[0]

            if loc[1] > WINDOW_SIZE[1]: loc[1] = 0
            if loc[0] > WINDOW_SIZE[0]: loc[0] = 0

    def draw(self, surf, color=(70, 70, 70)):
        [pygame.draw.circle(surf, pygame.Color(color), loc, 3) for loc in self.locs]


class Bullet:
    image = pygame.image.load('assets/Bullet.png').convert()
    image.set_colorkey((0, 0, 0))
    image = pygame.transform.scale(image, (SPRITE_SIZE, SPRITE_SIZE))
    rect = image.get_rect()
    locs = []
    speed = 12

    def __init__(self, rectx, recty, direcao):
        if direcao < 5:
            self.locs.append([rectx, recty, direcao, 0])

    def update(self, dt, surf):
        for loc in self.locs:
            # 1 - UP; 2 - LEFT; 3 - DOWN; 4 - RIGHT;
            if loc[2] == 1: loc[1] -= round(self.speed * dt)
            elif loc[2] == 2: loc[0] -= round(self.speed * dt)
            elif loc[2] == 3: loc[1] += round(self.speed * dt)
            elif loc[2] == 4: loc[0] += round(self.speed * dt)

            if loc[0] > WINDOW_SIZE[0] + 1: self.locs.remove(loc)
            if loc[0] < 0 - self.rect.height: self.locs.remove(loc)
            if loc[1] > WINDOW_SIZE[1] + 1: self.locs.remove(loc)
            if loc[1] < 0 - self.rect.height: self.locs.remove(loc)

            self.rect[0] = loc[0]
            self.rect[1] = loc[1]
            self.draw(surf)

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Player:
    shot_delay = 0.25
    moving_right = False
    moving_left = False
    moving_up = False
    moving_down = False
    firing = False
    rect = pygame.math.Vector2()

    def __init__(self, pos):
        self.last_time = time()
        self.last_shot = self.last_time
        self.sprites = []
        for i in range(1, 3):
            self.sprite = pygame.image.load(f'assets/player_idle{i}.png').convert()
            self.sprite = pygame.transform.scale(self.sprite, (SCALED_SPRITE_SIZE, 24*4))
            self.sprite.set_colorkey((0, 0, 0))
            self.sprites.append(self.sprite)
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(center=pos)
        self.movement = pygame.math.Vector2()
        self.speed = 7

    def animate(self):
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def get_input(self, event):
        if event.key in CONTROLS['LEFT']:
            self.moving_left = True
        if event.key in CONTROLS['RIGHT']:
            self.moving_right = True
        if event.key in CONTROLS['DOWN']:
            self.moving_down = True
        if event.key in CONTROLS['UP']:
            self.moving_up = True
        if event.key in CONTROLS['FIRE']:
            self.firing = True

    def get_input_keyup(self, event):
        if event.key in CONTROLS['LEFT']:
            self.moving_left = False
        if event.key in CONTROLS['RIGHT']:
            self.moving_right = False
        if event.key in CONTROLS['DOWN']:
            self.moving_down = False
        if event.key in CONTROLS['UP']:
            self.moving_up = False
        if event.key in CONTROLS['FIRE']:
            self.firing = False

    def fire(self):
        Bullet(self.rect.center[0] - SPRITE_SIZE / 2, self.rect.center[1] - SPRITE_SIZE, 1)

    def update(self, dt, last_time):
        self.last_time = last_time
        if self.moving_right: self.rect[0] += round(self.speed * dt)
        if self.moving_left: self.rect[0] -= round(self.speed * dt)
        if self.moving_up: self.rect[1] -= round(self.speed * dt)
        if self.moving_down: self.rect[1] += round(self.speed * dt)

        if self.firing and self.last_time - self.last_shot > self.shot_delay: self.fire(); self.last_shot = self.last_time

        if self.rect[0] > WINDOW_SIZE[0] - self.rect.height: self.rect[0] = WINDOW_SIZE[0] - self.rect.height
        if self.rect[0] < 0: self.rect[0] = 0
        if self.rect[1] > WINDOW_SIZE[1] - self.rect.height: self.rect[1] = WINDOW_SIZE[1] - self.rect.height
        if self.rect[1] < 0: self.rect[1] = 0

        self.animate()

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Enemy1:  # Placeholder enemy
    instancelist = []
    speed = WINDOW_SIZE[1] * 0.004

    def __init__(self, pos):
        self.x, self.y = pos
        self.instancelist.append(self)
        self.sprites = []
        for i in range(1, 3):
            self.sprite = pygame.image.load(f'assets/enemy_idle{i}.png').convert()
            self.sprite = pygame.transform.flip(self.sprite, False, True)
            self.sprite = pygame.transform.scale(self.sprite, (SCALED_SPRITE_SIZE, SCALED_SPRITE_SIZE))
            self.sprite.set_colorkey((0, 0, 0))
            self.sprites.append(self.sprite)
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.direction = choice([True, False])
        self.y_direction = False

    def animate(self):
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def death(self):
        for bloc in Bullet.locs:
            if self.x - self.rect.width/2 < bloc[0] < self.x+10 + self.rect.height and self.y - self.rect.height < bloc[1] < self.y + self.rect.height:
                self.instancelist.remove(self)
                Bullet.locs.remove(bloc)

    def move(self, dt):
        if randint(0, 2000) < 1:
            self.y_direction = True
            self.old_y = self.y
        if self.y_direction:
            if self.y < self.old_y + SCALED_SPRITE_SIZE:
                self.y += self.speed * dt
            else: self.y_direction = False
        else:
            if self.direction:
                self.x += self.speed * dt
                if self.x > WINDOW_SIZE[0]-100:
                    self.direction = False
            else:
                self.x -= self.speed * dt
                if self.x < 5:
                    self.direction = True

    def update(self, dt, surf):
        self.death()
        self.move(dt)

        self.rect[0] = self.x
        self.rect[1] = self.y

        self.animate()
        self.draw(surf)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    @staticmethod
    def spawn_enemy(n):
        for i in range(1, n):
            x = randint(0, WINDOW_SIZE[0])
            y = WINDOW_SIZE[1]/2 - 300
            Enemy1((x, y))



