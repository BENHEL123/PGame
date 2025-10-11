# TASK 5.1
import time

import pygame as pg
import random

# здесь определяются константы, функции и классы
FPS = 60
WIDTH, HEIGHT = 1000, 600
R = 60
ORANGE = (255, 150, 100)
PINK = (255, 210, 210)

# здесь происходит инициализация, создание объектов
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # также здесь можно указать битовые флаги
pg.display.set_caption("Игра")
clock = pg.time.Clock()


def circ():
    screen.fill(PINK)
    x1 = random.randint(R, WIDTH - R)
    y1 = random.randint(R, HEIGHT - R)
    pg.draw.circle(screen, ORANGE, (x1, y1), R)
    return x1, y1


# если надо до цикла отобразить какие-то объекты, обновляем экран
x, y = circ()
flag_pop = False
pg.display.update()

# главный цикл
flag_play = True
while flag_play:
    # настраиваем частоту итераций в секунду
    clock.tick(FPS)

    # цикл обработки событий
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            flag_play = False
            break
    if not flag_play:
        break
    pressed = pg.mouse.get_pressed()
    if pressed[1]:
        if not flag_pop:
            current_pos = pg.mouse.get_pos()
            print(current_pos)
            if (x - R <= current_pos[0] <= x + R) and (y - R <= current_pos[1] <= y + R):
                flag_pop = True
        if flag_pop:
            x, y = circ()
            print(x, y)
            flag_pop = False

    # изменение объектов
    # ...

    # обновление экрана
    pg.display.update()
