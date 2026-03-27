import numpy as np
from constants.global_var import config
from game_engine import g_engine
from classes.Boss import Boss

def get_current_ai_state():
    """
        17-sensor radar for the AI.
        Returns a numpy array with the current game state.
    """
    w, h = config.INTERNAL_RESOLUTION

    if g_engine.player:
        px = float(g_engine.player.rect.centerx)
        py = float(g_engine.player.rect.centery)
    else:
        px = w / 2.0
        py = h / 2.0

    # 1) Enemy positions (dx, dy) normalized to [-1, 1] based on screen size
    enemy_list = []
    for e in g_engine.all_enemies:
        d = (e.rect.centerx - px) ** 2 + (e.rect.centery - py) ** 2
        enemy_list.append((d, e))

    enemy_list.sort(key=lambda x: x[0])

    dx_e1, dy_e1 = 2.0, 2.0
    dx_e2, dy_e2 = 2.0, 2.0

    if len(enemy_list) >= 1:
        e = enemy_list[0][1]
        dx_e1 = np.clip((e.rect.centerx - px) / w, -1.0, 1.0)
        dy_e1 = np.clip((e.rect.centery - py) / h, -1.0, 1.0)

    if len(enemy_list) >= 2:
        e = enemy_list[1][1]
        dx_e2 = np.clip((e.rect.centerx - px) / w, -1.0, 1.0)
        dy_e2 = np.clip((e.rect.centery - py) / h, -1.0, 1.0)

    # 2) Power-up positions (dx, dy) normalized to [-1, 1]
    dx_pu, dy_pu = 2.0, 2.0
    min_pu_dist = float("inf")
    for pu in g_engine.powerups:
        d = (pu.rect.centerx - px) ** 2 + (pu.rect.centery - py) ** 2
        if d < min_pu_dist:
            min_pu_dist = d
            dx_pu = np.clip((pu.rect.centerx - px) / w, -1.0, 1.0)
            dy_pu = np.clip((pu.rect.centery - py) / h, -1.0, 1.0)

    # 3) Bullet proximity in 3 zones (left, center, right)
    dl, dc, dr = 1.0, 1.0, 1.0

    if g_engine.enemy_bullets.active_count > 0:
        n = g_engine.enemy_bullets.active_count
        b_xs = g_engine.enemy_bullets.pos[:n, 0]
        b_ys = g_engine.enemy_bullets.pos[:n, 1]

        diff_y = py - b_ys
        diff_x = b_xs - px

        danger_mask = (diff_y > -20) & (diff_y < 400)

        if np.any(danger_mask):
            valid_dy = diff_y[danger_mask]
            valid_dx = diff_x[danger_mask]
            norm_dist = np.clip(valid_dy / 400.0, 0.0, 1.0)

            left_mask = (valid_dx > -80) & (valid_dx < -20)
            center_mask = (valid_dx >= -20) & (valid_dx <= 20)
            right_mask = (valid_dx > 20) & (valid_dx < 80)

            if np.any(left_mask):
                dl = float(np.min(norm_dist[left_mask]))
            if np.any(center_mask):
                dc = float(np.min(norm_dist[center_mask]))
            if np.any(right_mask):
                dr = float(np.min(norm_dist[right_mask]))

    wall_l = float(np.clip(px / w, 0.0, 1.0))
    wall_r = float(np.clip((w - px) / w, 0.0, 1.0))
    wall_t = float(np.clip(py / h, 0.0, 1.0))
    wall_b = float(np.clip((h - py) / h, 0.0, 1.0))

    enemy_count_norm = float(min(len(g_engine.all_enemies) / 12.0, 1.0))
    boss_present = 1.0 if any(isinstance(e, Boss) for e in g_engine.all_enemies) else 0.0

    return np.array([
        px / w, py / h,
        dx_e1, dy_e1,
        dx_e2, dy_e2,
        dx_pu, dy_pu,
        dl, dc, dr,
        wall_l, wall_r, wall_t, wall_b,
        enemy_count_norm, boss_present,
    ], dtype=np.float32)