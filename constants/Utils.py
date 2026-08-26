import os
import platform
import pygame
from time import time

pygame.init()


def delta_time(last_time):
    now = time()
    dt = now - last_time
    last_time = now
    return dt, last_time


def get_user_data_dir():
    """Per-user, writable directory to store save data (settings, high score)."""
    app_name = "ShootEmUp"
    system = platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")

    path = os.path.join(base, app_name)
    os.makedirs(path, exist_ok=True)
    return path


def get_high_score():
    try:
        with open(os.path.join(get_user_data_dir(), "highscore.txt"), "r") as f:
            return int(f.read())
    except (OSError, ValueError):
        return 0


def save_high_score(score):
    with open(os.path.join(get_user_data_dir(), "highscore.txt"), "w") as f:
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
