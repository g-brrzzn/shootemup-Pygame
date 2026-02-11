import pygame
from random import choice, randint
from game_engine import g_engine
from constants.global_var import config, SCALED_SPRITE_SIZE
from classes.Enemy import Enemy1, Enemy2, Enemy3

class FormationManager:
    @staticmethod
    def spawn_formation(formation_type, level_difficulty):
        width = config.INTERNAL_RESOLUTION[0]
        EnemyClass = Enemy1
        formation_count = 5 
        
        if level_difficulty > 2 and randint(0, 10) > 6: 
            EnemyClass = Enemy2
            formation_count = 3 
            
        if level_difficulty > 4 and randint(0, 10) > 8: 
            EnemyClass = Enemy3
            formation_count = 2 

        if formation_type == 'V_SHAPE':
            spacing_x = 80 if EnemyClass == Enemy1 else 120
            spacing_y = 50
            safe_margin = spacing_x * 2 + 50
            center_x = randint(safe_margin, width - safe_margin)
            start_y = -100
            if formation_count % 2 == 0: formation_count += 1
            mid_index = formation_count // 2
            
            for i in range(formation_count):
                offset = abs(i - mid_index) 
                x = center_x + (i - mid_index) * spacing_x
                y = start_y - (offset * spacing_y)
                EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)

        elif formation_type == 'LINE_HORIZONTAL':
            gap = width // (formation_count + 1)
            y = -50
            for i in range(formation_count):
                x = gap * (i + 1)
                EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)

        elif formation_type == 'DIAGONAL_LEFT':
            start_x = randint(20, width // 2 - 100)
            start_y = -50
            for i in range(formation_count):
                EnemyClass((start_x + i*70, start_y - i*60), g_engine.all_enemies, g_engine.all_sprites)

        elif formation_type == 'DIAGONAL_RIGHT':
            start_x = randint(width // 2 + 100, width - 20)
            start_y = -50
            for i in range(formation_count):
                EnemyClass((start_x - i*70, start_y - i*60), g_engine.all_enemies, g_engine.all_sprites)
        
        elif formation_type == 'CIRCLE_CLUSTER':
            EnemyClass = Enemy1
            center_x = randint(150, width - 150)
            center_y = -150
            radius = 80 
            EnemyClass((center_x, center_y), g_engine.all_enemies, g_engine.all_sprites)
            for i in range(5): 
                angle = (i / 5) * 6.28 
                x = center_x + int(pygame.math.Vector2(radius, 0).rotate_rad(angle).x)
                y = center_y + int(pygame.math.Vector2(radius, 0).rotate_rad(angle).y)
                EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)

        elif formation_type == 'RANDOM_RAIN':
            count = 6 + int(level_difficulty)
            if EnemyClass == Enemy2: count = 4
            if EnemyClass == Enemy3: count = 2
            
            for _ in range(count):
                x = randint(30, width - 30)
                y = randint(-400, -50) 
                EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)