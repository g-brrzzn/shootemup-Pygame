import pygame
import numpy as np
import random
from game_engine import g_engine
from constants.global_var import config
from classes.Boss import Boss

class CollisionManager:
    
    @staticmethod
    def update():
        if not g_engine.player or g_engine.player.getLife() <= 0:
            return

        CollisionManager._check_enemy_bullets_vs_player()
        CollisionManager._check_enemy_bullets_vs_shields()
        CollisionManager._check_player_bullets_vs_enemies()
        CollisionManager._check_player_vs_powerups()
        CollisionManager._check_player_vs_enemies()

    @staticmethod
    def _check_enemy_bullets_vs_player():
        if g_engine.enemy_bullets.active_count <= 0:
            return

        p_rect = g_engine.player.hitbox
        parry_rect = g_engine.player.parry_rect 
        bullets_to_kill = set()

        n = g_engine.enemy_bullets.active_count
        b_x = g_engine.enemy_bullets.pos[:n, 0]
        b_y = g_engine.enemy_bullets.pos[:n, 1]

        not_grazed = ~g_engine.enemy_bullets.grazed[:n]
        grazes = np.nonzero(
            (b_x >= p_rect.left - 40) & (b_x <= p_rect.right + 40) &
            (b_y >= p_rect.top - 40) & (b_y <= p_rect.bottom + 40) &
            not_grazed
        )[0]

        for g in grazes:
            g_engine.enemy_bullets.grazed[g] = True
            g_engine.score += 10
            g_engine.spark_system.emit(
                pos=(g_engine.enemy_bullets.pos[g, 0], g_engine.enemy_bullets.pos[g, 1]),
                angle=random.randint(0, 360),
                speed=random.randint(3, 7),
                color=(100, 200, 255),
                scale=1.2,
            )

        if g_engine.player.parry_active:
            possible_parrys = np.nonzero(
                (b_x >= parry_rect.left) & (b_x <= parry_rect.right) &
                (b_y >= parry_rect.top) & (b_y <= parry_rect.bottom)
            )[0]
            
            parried_this_frame = False 
            
            for h in possible_parrys:
                meta = g_engine.enemy_bullets.get_bullet_meta(h)
                if meta.get("is_pink") and h not in bullets_to_kill:
                    g_engine.score += 150
                    g_engine.player.gain_exp(1)
                    parried_this_frame = True 
                    bullets_to_kill.add(h)
                    
            if parried_this_frame:
                g_engine.player.on_parry_success() 

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


    @staticmethod
    def _check_enemy_bullets_vs_shields():
        if g_engine.enemy_bullets.active_count <= 0 or g_engine.player_bullets.active_count <= 0:
            return

        p_n = g_engine.player_bullets.active_count
        shields = [i for i in range(p_n) if g_engine.player_bullets.meta[i].get("is_shield")]

        if not shields:
            return

        e_n = g_engine.enemy_bullets.active_count
        e_x = g_engine.enemy_bullets.pos[:e_n, 0]
        e_y = g_engine.enemy_bullets.pos[:e_n, 1]
        bullets_to_kill = set()

        for si in shields:
            sx, sy = g_engine.player_bullets.pos[si]
            
            dist_sq = (e_x - sx)**2 + (e_y - sy)**2
            hits = np.nonzero(dist_sq < 400)[0] 

            for h in hits:
                if h not in bullets_to_kill:
                    bullets_to_kill.add(h)
                    g_engine.spark_system.emit(
                        pos=(e_x[h], e_y[h]),
                        angle=random.randint(0, 360), speed=random.randint(3, 7),
                        color=(100, 200, 255), scale=0.8
                    )

        for h in sorted(list(bullets_to_kill), reverse=True):
            g_engine.enemy_bullets.kill_bullet(h)


    @staticmethod
    def _check_player_bullets_vs_enemies():
        if g_engine.player_bullets.active_count <= 0 or len(g_engine.all_enemies) <= 0:
            return

        n = g_engine.player_bullets.active_count
        b_x = g_engine.player_bullets.pos[:n, 0]
        b_y = g_engine.player_bullets.pos[:n, 1]
        bullets_to_kill = set()

        for enemy in list(g_engine.all_enemies):
            ex, ey, ew, eh = enemy.rect.x, enemy.rect.y, enemy.rect.width, enemy.rect.height
            
            hits = np.nonzero(
                (b_x >= ex) & (b_x <= ex + ew) & (b_y >= ey) & (b_y <= ey + eh)
            )[0]

            valid_hits = [h for h in hits if h not in bullets_to_kill]

            if valid_hits:
                took_damage = False
                for h in valid_hits:
                    meta = g_engine.player_bullets.meta[h]
                    if not meta.get("indestructible"):
                        bullets_to_kill.add(h)
                        took_damage = True
                    elif meta.get("orbit"):
                        curr_t = pygame.time.get_ticks()
                        if curr_t - getattr(enemy, 'last_orbit_hit', 0) >= 150:
                            enemy.last_orbit_hit = curr_t
                            took_damage = True
                    else:
                        took_damage = True

                if took_damage:
                    if isinstance(enemy, Boss):
                        g_engine.explosion_system.create(
                            enemy.rect.centerx,
                            enemy.rect.centery + random.randint(-20, 20),
                        )
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

    @staticmethod
    def _check_player_vs_powerups():
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
            elif powerup.p_type == "ricochet":
                g_engine.player.activate_ricochet()
            pygame.mixer.Sound.play(g_engine.assets.get_sound("power-up"))

    @staticmethod
    def _check_player_vs_enemies():
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