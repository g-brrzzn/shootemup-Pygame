import pygame
from time import time
from .global_var import FRAME_RATE

pygame.init()


def delta_time(last_time):
    now = time()
    dt = now - last_time
    last_time = now
    return dt, last_time


def get_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0


def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))


def create_glow_surface(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    max_intensity = 60

    for r in range(radius, 0, -1):
        dist_norm = r / radius
        power = 1 - dist_norm
        factor = (power**2) * (max_intensity / 255.0)
        red = int(color[0] * factor)
        green = int(color[1] * factor)
        blue = int(color[2] * factor)
        pygame.draw.circle(surf, (red, green, blue, 255), (radius, radius), r)
    return surf
