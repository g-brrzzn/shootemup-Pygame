import pygame
from time import time
from .global_var import (
    FRAME_RATE
)
pygame.init()


def delta_time(last_time):
    dt = time() - last_time
    dt *= FRAME_RATE
    last_time = time()
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