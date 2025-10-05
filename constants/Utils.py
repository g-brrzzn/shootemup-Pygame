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

