import pygame
from random import choice, randint
from game_engine import g_engine
from constants.global_var import config
from classes.Enemy import Enemy1, Enemy2, Enemy3

class FormationManager:
    @staticmethod
    def _spawn_v_shape(width, EnemyClass, count, level_difficulty):
        spacing_x = 80 if EnemyClass == Enemy1 else 120
        spacing_y = 50
        safe_margin = spacing_x * 2 + 50
        
        safe_margin = min(safe_margin, width // 3) 
        center_x = randint(safe_margin, width - safe_margin)
        start_y = -100
        
        if count % 2 == 0: 
            count += 1
            
        mid_index = count // 2
        
        for i in range(count):
            offset = abs(i - mid_index) 
            x = center_x + (i - mid_index) * spacing_x
            y = start_y - (offset * spacing_y)
            EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)

    @staticmethod
    def _spawn_line_horizontal(width, EnemyClass, count, level_difficulty):
        gap = width // (count + 1)
        y = -50
        for i in range(count):
            x = gap * (i + 1)
            EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)

    @staticmethod
    def _spawn_diagonal_left(width, EnemyClass, count, level_difficulty):
        start_x = randint(20, width // 2 - 100)
        start_y = -50
        for i in range(count):
            EnemyClass((start_x + i * 70, start_y - i * 60), g_engine.all_enemies, g_engine.all_sprites)

    @staticmethod
    def _spawn_diagonal_right(width, EnemyClass, count, level_difficulty):
        start_x = randint(width // 2 + 100, width - 20)
        start_y = -50
        for i in range(count):
            EnemyClass((start_x - i * 70, start_y - i * 60), g_engine.all_enemies, g_engine.all_sprites)
    
    @staticmethod
    def _spawn_circle_cluster(width, EnemyClass, count, level_difficulty):
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

    @staticmethod
    def _spawn_random_rain(width, EnemyClass, count, level_difficulty):
        actual_count = 6 + int(level_difficulty)
        if EnemyClass == Enemy2: actual_count = 4
        if EnemyClass == Enemy3: actual_count = 2
        
        for _ in range(actual_count):
            x = randint(30, width - 30)
            y = randint(-400, -50) 
            EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)

    @staticmethod
    def _spawn_enter_and_stop(width, EnemyClass, count, level_difficulty):
        gap = width // (count + 1)
        for i in range(count):
            x = gap * (i + 1)
            y = -50 - (i * 30)
            enemy = EnemyClass((x, y), g_engine.all_enemies, g_engine.all_sprites)
            
            def custom_move(e, dt):
                import math
                target_y = 80 + (e.random_offset % 60)
                if e.y < target_y:
                    e.y += e.base_speed * 1.5 * dt
                else:
                    e.x += math.sin(pygame.time.get_ticks() * 0.001 + e.random_offset) * 30 * dt

            enemy.custom_move_func = custom_move

    @staticmethod
    def _spawn_sweep_cross(width, EnemyClass, count, level_difficulty):
        side = choice(['left', 'right'])
        start_x = -50 if side == 'left' else width + 50
        direction = 1 if side == 'left' else -1
        
        for i in range(count):
            y = -50 - (i * 60)
            enemy = EnemyClass((start_x, y), g_engine.all_enemies, g_engine.all_sprites)
            enemy.direction = direction
            
            def custom_move(e, dt):
                e.y += e.base_speed * 0.4 * dt
                e.x += getattr(e, 'direction', 1) * 350 * dt

            enemy.custom_move_func = custom_move

    @staticmethod
    def _spawn_pincer(width, EnemyClass, count, level_difficulty):
        FormationManager._spawn_diagonal_left(width, EnemyClass, max(2, count // 2), level_difficulty)
        FormationManager._spawn_diagonal_right(width, EnemyClass, max(2, count // 2), level_difficulty)

    @staticmethod
    def _spawn_blockade(width, EnemyClass, count, level_difficulty):
        gap = width // (count + 1)
        for i in range(count):
            EnemyClass((gap * (i + 1), -50), g_engine.all_enemies, g_engine.all_sprites)
            EnemyClass((gap * (i + 1), -130), g_engine.all_enemies, g_engine.all_sprites)

    @staticmethod
    def _spawn_crossfire(width, EnemyClass, count, level_difficulty):
        for side, direction, start_x in [('left', 1, -50), ('right', -1, width + 50)]:
            for i in range(max(2, count // 2)):
                y = -50 - (i * 60)
                enemy = EnemyClass((start_x, y), g_engine.all_enemies, g_engine.all_sprites)
                enemy.direction = direction
                
                def custom_move(e, dt):
                    e.y += e.base_speed * 0.4 * dt
                    e.x += getattr(e, 'direction', 1) * 350 * dt

                enemy.custom_move_func = custom_move

    FORMATIONS = {
        'V_SHAPE': _spawn_v_shape,
        'LINE_HORIZONTAL': _spawn_line_horizontal,
        'DIAGONAL_LEFT': _spawn_diagonal_left,
        'DIAGONAL_RIGHT': _spawn_diagonal_right,
        'CIRCLE_CLUSTER': _spawn_circle_cluster,
        'RANDOM_RAIN': _spawn_random_rain,
        'ENTER_AND_STOP': _spawn_enter_and_stop,
        'SWEEP_CROSS': _spawn_sweep_cross,
        'PINCER': _spawn_pincer,
        'BLOCKADE': _spawn_blockade,
        'CROSSFIRE': _spawn_crossfire,
    }
    
    @staticmethod
    def spawn_formation(formation_type, level_difficulty):
        width = config.INTERNAL_RESOLUTION[0]
        
        EnemyClass = Enemy1
        formation_count = 5 
        
        if formation_type == 'ENTER_AND_STOP':
            EnemyClass = choice([Enemy2, Enemy3])
            formation_count = 3 if EnemyClass == Enemy2 else 2
        elif formation_type in ['SWEEP_CROSS', 'CROSSFIRE']:
            EnemyClass = Enemy1
            formation_count = 6
        elif formation_type == 'BLOCKADE':
            EnemyClass = choice([Enemy1, Enemy2])
            formation_count = 4 if EnemyClass == Enemy1 else 2
        elif formation_type == 'PINCER':
            EnemyClass = Enemy1
            formation_count = 6
        else:
            if level_difficulty > 2 and randint(0, 10) > 6: 
                EnemyClass = Enemy2
                formation_count = 3 
                
            if level_difficulty > 4 and randint(0, 10) > 8: 
                EnemyClass = Enemy3
                formation_count = 2 

        if formation_type in FormationManager.FORMATIONS:
            spawn_func = FormationManager.FORMATIONS[formation_type]
            spawn_func(width, EnemyClass, formation_count, level_difficulty)
        else:
            FormationManager._spawn_line_horizontal(width, EnemyClass, formation_count, level_difficulty)