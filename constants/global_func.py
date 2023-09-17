from constants.global_var import *
from constants.global_imports import *

pygame.init()
screen = pygame.display.set_mode(config.window_size)
font = pygame.font.Font('assets/American Captain.ttf', 42)
gameplay_font = pygame.font.Font('assets/American Captain.ttf', 32)


def text(string, x, y, color=(200, 200, 200), original_font=True):
    string = str(string)
    if original_font: info = font.render(string, True, color)
    else:             info = gameplay_font.render(string, True, color)
    textrect = info.get_rect()
    textrect.center = (x, y)
    screen.blit(info, textrect)


def bool2Switch(bool):
    if bool: return 'ON'
    else:    return 'OFF'


def delta_time(last_time):
    dt = time() - last_time
    dt *= FRAME_RATE
    last_time = time()
    return dt, last_time


def find_key_by_value(dict, target_value):
    for key, value in dict.items():
        if value == target_value:
            return key
    return None


def vertical(surf, is_square=True, start_color=BACKGROUND_COLOR_1, end_color=BACKGROUND_COLOR_2):
    if not is_square:
        size = config.window_size
        axis_x, axis_y = 0, 0
    else:
        size = (400, 400)
        center = (config.window_size[0] / 2, config.window_size[1] / 2)
        x, y = center
        axis_x = x - size[0] / 2
        axis_y = y - size[1] / 2

    height = size[1]
    big_surf = pygame.Surface((1, height)).convert_alpha()
    dd = 1.0 / height
    sr, sg, sb, sa = start_color
    er, eg, eb, ea = end_color
    rm = (er - sr) * dd
    gm = (eg - sg) * dd
    bm = (eb - sb) * dd
    am = (ea - sa) * dd
    for y in range(height):
        big_surf.set_at((0, y),
                       (int(sr + rm * y),
                        int(sg + gm * y),
                        int(sb + bm * y),
                        int(sa + am * y)))
    v = pygame.transform.scale(big_surf, size)
    surf.blit(v, (axis_x, axis_y))


class Fall:
    def __init__(self, quantidade):
        self.locs = []
        for i in range(quantidade):
            snowloc = [randint(1, config.window_size[0] - 1), randint(1, config.window_size[1] - 1)]
            self.locs.append(snowloc)

    def update(self, gravity=0.3, wind=0.3):
        for loc in self.locs:
            loc[1] += gravity + uniform(0.1, 0.9)

            if wind > 0:
                loc[0] += wind
            if gravity < 0:
                if loc[1] < 0: loc[1] = config.window_size[1]
                if loc[0] < 0: loc[0] = config.window_size[0]

            if loc[1] > config.window_size[1]: loc[1] = 0
            if loc[0] > config.window_size[0]: loc[0] = 0

    def draw(self, surf, color=(70, 70, 70)):
        [pygame.draw.circle(surf, pygame.Color(color), loc, 3) for loc in self.locs]




def MenuMaker(options, title, selected, surf):
    vertical(surf)
    for i in range(200):
        pygame.draw.line(surf, BACKGROUND_COLOR_MENU_1,
                         (config.window_size[0] / 2 - 100 + i, config.window_size[1] / 2 - 179),      # Title background
                         (config.window_size[0] / 2 - 100 + i, config.window_size[1] / 2 - 230), 4)   # Title background
    text(title, config.window_size[0] / 2, config.window_size[1] / 2 - 200)

    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 180),      # Title Bottom outline
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 180), 4)   # Title Bottom outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 179),      # Title Top-left outline
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 230), 4)   # Title Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 179),      # Title Top-right outline
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 230), 4)   # Title Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 230),      # Title Top outline
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 230), 4)   # Title Top outline

    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 200),      # Top-right outline
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 - 200), 4)   # Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 200),      # Top-left outline
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 - 200), 4)   # Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 - 200),      # Left outline
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 + 200), 4)   # Left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 - 200),      # Right outline
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 + 200), 4)   # Right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 + 200),      # Bottom outline
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 + 200), 4)   # Bottom outline

    if len(options) >= 4: y_gap = 90
    elif len(options) >= 6: y_gap = 120
    else: y_gap = 50

    for option in options:
        if selected == options.index(option):
            text(option, config.window_size[0] / 2, (config.window_size[1] / 2 - y_gap) + 50 * options.index(option), (100, 40, 80))
            if len(option) < 10:
                text('|', config.window_size[0] / 2 + 100, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
                text('|', config.window_size[0] / 2 - 100, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
            elif len(option) < 20:
                text('|', config.window_size[0] / 2 + 150, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
                text('|', config.window_size[0] / 2 - 150, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
            else:
                text('|', config.window_size[0] / 2 + 180, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
                text('|', config.window_size[0] / 2 - 180, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
        else:
            text(option, config.window_size[0] / 2, (config.window_size[1] / 2 - y_gap) + 50 * options.index(option))


