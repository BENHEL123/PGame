import pygame as pg
import random
import time

FPS = 60
WIDTH, HEIGHT = 600, 500
MINT = (230, 254, 212)
ORANGE = (255, 150, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FIRE = (245, 112, 37)
DARK_BROWN = (110, 7, 7)
BROWN = (166, 13, 13)
GREEN = (0, 204, 102)
BLUE = (0, 128, 255)
LIGHT_BLUE = (21, 219, 219)
DARK_GREEN = (0, 102, 0)
GRAY = (160, 160, 160)
COLORS = MINT, ORANGE, WHITE, BLACK, FIRE, BROWN, GREEN, BLUE, LIGHT_BLUE, DARK_GREEN, GRAY

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Игра")
clock = pg.time.Clock()

# до начала игрового цикла отображаем объекты:
# координаты центра круга
x, y = WIDTH / 2, HEIGHT / 2  # координаты центра круга
r = 30  # радиус круга
present_color = ORANGE
counter = 0
pg.draw.circle(screen, ORANGE, (x, y), r)  # рисуем круг
pg.display.update()  # обновляем окно

flag_play = True
while flag_play:
    clock.tick(FPS)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            flag_play = False
            break
    if not flag_play:
        break

    if 0 < x < WIDTH and y < r:
        y += 3
    if x > WIDTH - r and 0 < y < HEIGHT:
        x -= 3
    if 0 < x < WIDTH and y > HEIGHT - r:
        y -= 3
    if x < 0 + r and 0 < y < HEIGHT - r:
        x += 3

    # изменение состояний объектов:
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT]:
        x -= 3
    if keys[pg.K_RIGHT]:
        x += 3
    if keys[pg.K_UP]:
        y -= 3
    if keys[pg.K_DOWN]:
        y += 3
    if keys[pg.K_SPACE]:
        counter += 1
        if counter == 10:
            present_color = random.choice(COLORS)
        elif counter >= 10:
            counter = 0
    screen.fill(MINT)  # заливаем фон, стирая предыдущий круг
    pg.draw.circle(screen, present_color, (x, y), r)  # рисуем новый, сдвинутый круг

    pg.display.update()  # обновляем окно
