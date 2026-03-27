import gymnasium as gym
from gymnasium import spaces
import numpy as np

from Game import Game
from game_engine import g_engine
from constants.global_var import config

from reinforcement_learning.ai_state import get_current_ai_state

class ShootEmUpEnv(gym.Env):
    def __init__(self, stage="full", frame_skip=3, **kwargs):
        super().__init__()

        self.stage = stage
        self.frame_skip = frame_skip

        self.game = Game(ai_stage=stage)

        self.action_space = spaces.MultiDiscrete([3, 3])

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(17,), dtype=np.float32
        )

        self.previous_px = None
        self.previous_py = None
        self.previous_wall_dist = None
        self.previous_enemy_dist = None

        self.idle_steps = 0
        self.edge_steps = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.game.start()
        obs = get_current_ai_state()

        self.previous_px = obs[0]
        self.previous_py = obs[1]
        self.previous_wall_dist = min(obs[11:15])
        self.previous_enemy_dist = None

        self.idle_steps = 0
        self.edge_steps = 0

        return obs, {}

    def step(self, action):
        for _ in range(3):
            if g_engine.player and g_engine.player.getLife() > 0:
                g_engine.player.apply_ai_action(action)

            self.game.update()

        obs = get_current_ai_state()

        px, py = obs[0], obs[1]
        dx_e, dy_e = obs[2], obs[3]
        dx_pu, dy_pu = obs[6], obs[7]
        dl, dc, dr = obs[8], obs[9], obs[10]
        wall_l, wall_r, wall_t, wall_b = obs[11:15]

        w, h = config.INTERNAL_RESOLUTION

        reward = -0.002

        player_alive = g_engine.player and g_engine.player.getLife() > 0

        if player_alive:
            # MOVEMENT / INERTIA
            movement = abs(px - self.previous_px) + abs(py - self.previous_py)

            if movement < 0.003:
                self.idle_steps += 1
            else:
                self.idle_steps = 0
                reward += 0.01

            if self.idle_steps > 10:
                reward -= 0.05

            # WALLS / CORNER
            x_edge = min(px, 1.0 - px)
            y_edge = min(py, 1.0 - py)

            min_wall = min(wall_l, wall_r, wall_t, wall_b)

            if min_wall < 0.08:
                self.edge_steps += 1
                reward -= (0.08 - min_wall) * 1.2
            else:
                self.edge_steps = 0

            # corner penalty (strong)
            if x_edge < 0.14 and y_edge < 0.18:
                corner_penalty = (0.14 - x_edge) + (0.18 - y_edge)
                reward -= corner_penalty * 1.5

            # reward for leaving the wall
            if self.previous_wall_dist is not None:
                if min_wall > self.previous_wall_dist + 0.01:
                    reward += 0.02
 
            # BULLETS (threat)
            nearest_bullet = min(dl, dc, dr)
            bullet_threat = max(0.0, 0.4 - nearest_bullet)

            reward -= bullet_threat * 1.5

            # COMBAT
            enemy_present = not (dx_e == 2.0 and dy_e == 2.0)

            if enemy_present:
                enemy_dist = np.hypot(dx_e * w, dy_e * h)

                ideal_min = 140
                ideal_max = 300
                
                # FORBIDDEN ZONE (too close)
                if enemy_dist < 110:
                    reward -= 0.4

                # IDEAL DISTANCE
                elif ideal_min <= enemy_dist <= ideal_max:
                    reward += 0.08
                    reward += (1.0 - min(1.0, abs(dx_e))) * 0.02

                # TOO FAR
                elif enemy_dist > ideal_max:
                    reward += 0.01

                # VERTICAL POSITIONING
                if dy_e < 0:
                    reward += 0.025  # stay below the enemy
                else:
                    reward -= 0.06   # going up too much

                # FIRING ZONE (in front of enemy)
                enemy_front = dy_e < -0.05
                aligned_x = abs(dx_e) < 0.15

                if enemy_front and aligned_x:
                    reward -= 0.25

                # IMMINENT COLLISION (lateral)
                if abs(dx_e) < 0.08 and abs(dy_e) < 0.15:
                    reward -= 0.3

                # INTELLIGENT AGGRESSIVENESS
                if bullet_threat < 0.05 and ideal_min <= enemy_dist <= ideal_max:
                    reward += 0.03

            # POWERUP (secondary)
            if not (dx_pu == 2.0 and dy_pu == 2.0):
                power_dist = np.hypot(dx_pu * w, dy_pu * h)
                reward += max(0.0, 0.02 * (1.0 - min(1.0, power_dist / 600)))

            # LIFE
            if g_engine.player.getLife() <= 0:
                reward -= 100

        terminated = False

        if not player_alive:
            terminated = True

        self.previous_px = px
        self.previous_py = py
        self.previous_wall_dist = min(wall_l, wall_r, wall_t, wall_b)

        return obs, float(reward), terminated, False, {}

    def render(self):
        pass