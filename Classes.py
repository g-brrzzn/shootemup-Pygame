import pygame.image
from constants.global_var import *
from constants.global_imports import *
from constants.global_func import Explosion

pygame.init()
pygame.display.set_mode(config.window_size)


class Bullet:
    image = pygame.image.load('assets/Bullet.png').convert()
    image.set_colorkey((0, 0, 0))
    image = pygame.transform.scale(image, (SPRITE_SIZE, SPRITE_SIZE))
    rect = image.get_rect()
    locs = []
    enemylocs = []
    speed = 12
    enemyspeed = 4

    def __init__(self, rectx, recty, direction, isFromPlayer=True):
        if direction < 5:
            if isFromPlayer:
                self.locs.append([rectx, recty, direction, isFromPlayer])
            else: self.enemylocs.append([rectx, recty, direction, isFromPlayer])

    def moveBullets(self, loc, dt, surf):
        if loc[3]: speed = self.speed
        else:      speed = self.enemyspeed
        
        # 1 - UP; 2 - LEFT; 3 - DOWN; 4 - RIGHT;
        if   loc[2] == 1: loc[1] -= round(speed * dt)
        elif loc[2] == 2: loc[0] -= round(speed * dt)
        elif loc[2] == 3: loc[1] += round(speed * dt)
        elif loc[2] == 4: loc[0] += round(speed * dt)

        if loc[3]:
            if loc[0] > config.window_size[0] + 1: self.locs.remove(loc)
            if loc[0] < 0 - self.rect.height: self.locs.remove(loc)
            if loc[1] > config.window_size[1] + 1: self.locs.remove(loc)
            if loc[1] < 0 - self.rect.height: self.locs.remove(loc)
        else: 
            if loc[0] > config.window_size[0] + 1: self.enemylocs.remove(loc)
            if loc[0] < 0 - self.rect.height: self.enemylocs.remove(loc)
            if loc[1] > config.window_size[1] + 1: self.enemylocs.remove(loc)
            if loc[1] < 0 - self.rect.height: self.enemylocs.remove(loc)

        self.rect[0] = loc[0]
        self.rect[1] = loc[1]
        self.draw(surf)
    
    def update(self, dt, surf):
        for loc in self.locs:
            self.moveBullets(loc, dt, surf)
        for loc in self.enemylocs:
            self.moveBullets(loc, dt, surf)

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Player:
    def __init__(self, pos):
        self.shot_delay = 0.25
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.firing = False
        self.rect = pygame.math.Vector2()
        
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
        self.life = MAX_LIFE

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
        if self.moving_right: self.rect[0]  +=  round(self.speed * dt)
        if self.moving_left: self.rect[0]   -=  round(self.speed * dt)
        if self.moving_up: self.rect[1]     -=  round(self.speed * dt)
        if self.moving_down: self.rect[1]   +=  round(self.speed * dt)

        if self.rect[0] > config.window_size[0] - self.rect.width: self.rect[0] = config.window_size[0] - self.rect.width
        if self.rect[0] < 0: self.rect[0] = 0
        if self.rect[1] > config.window_size[1] - self.rect.height: self.rect[1] = config.window_size[1] - self.rect.height
        if self.rect[1] < 0: self.rect[1] = 0
        
        if self.firing and self.last_time - self.last_shot > self.shot_delay: self.fire(); self.last_shot = self.last_time
        
        for e in Enemy1.instancelist:
            if self.rect.x - self.rect.width/2 < e.rect.x < self.rect.x + self.rect.width/2 and self.rect.y - self.rect.height/2 < e.rect.y < self.rect.y + self.rect.height/2:
                self.life -= 1

        for bloc in Bullet.enemylocs:
            if self.rect.x - self.rect.width/2+25 < bloc[0] < self.rect.x + self.rect.height/2 and self.rect.y - self.rect.height/2+30 < bloc[1] < self.rect.y + self.rect.height/2:
                self.life -= 1 
                Bullet.enemylocs.remove(bloc)
                
        self.animate()

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def getLife(self):       return self.life
    def setLife(self, life): self.life = life


class Enemy1:  # Placeholder enemy
    instancelist = []
    speed = config.window_size[1] * 0.004

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
        self.explosion = Explosion()

    def animate(self):
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def kill(self):
        self.instancelist.remove(self)

    def death(self):
        for bloc in Bullet.locs:
            if self.x - self.rect.width/2 < bloc[0] < self.x+10 + self.rect.height and self.y - self.rect.height < bloc[1] < self.y + self.rect.height:
                self.explosion.create(self.x, self.y)
                self.kill()
                Bullet.locs.remove(bloc)
                
    def shoot(self):
        if randint(0, 1000) < 2:
            Bullet(self.rect.center[0] - SPRITE_SIZE / 2, self.rect.center[1] - SPRITE_SIZE, 3, False)
              
    def move(self, dt):
        if randint(0, 1000) < 1:
            self.y_direction = True
            self.old_y = self.y
        if self.y_direction:
            if self.y < self.old_y + SCALED_SPRITE_SIZE:
                self.y += self.speed * dt
            else: self.y_direction = False
        else:
            if self.direction:
                self.x += self.speed * dt
                if self.x > config.window_size[0]-100:
                    self.direction = False
            else:
                self.x -= self.speed * dt
                if self.x < 5:
                    self.direction = True

    def update(self, dt, surf):
        self.death()
        self.move(dt)
        self.shoot()
        self.explosion.update(dt)
        self.explosion.draw(surf)

        self.rect[0] = self.x
        self.rect[1] = self.y

        self.animate()
        self.draw(surf)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    @staticmethod
    def spawn_enemy(n):
        for i in range(1, n):
            x = randint(0, config.window_size[0])
            y = config.window_size[1]/2 - 300
            Enemy1((x, y))



