# TASK 4.1
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

def random1():
    global WIDTH, HEIGHT, R
    x1 = random.randint(R, WIDTH - R)
    y1 = random.randint(R, HEIGHT - R)
    return x1, y1

def circ(x, y, R):
    screen.fill(PINK)
    pg.draw.circle(screen, ORANGE, (x, y), R)


# если надо до цикла отобразить какие-то объекты, обновляем экран
x, y = random1()
circ(x, y, R)
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
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 5:
                if R > 25:
                    R -= 2
                    circ(x, y, R)
            if event.button == 4:
                if R < 100:
                    R += 2
                    circ(x, y, R)
    if not flag_play:
        break
    pressed = pg.mouse.get_pressed()
    current_pos = pg.mouse.get_pos()
    distantion = (current_pos[0] - x) ** 2 + (current_pos[1] - y) ** 2
    distantion = distantion ** 0.5
    if distantion <= R:
        if pressed[1]:
            x, y = random1()
            circ(x, y, R)
            print(x, y)
        if pressed[0]:
            if R < 100:
                R += 2
                circ(x, y, R)
        if pressed[2]:
            if R > 25:
                R -= 2
                circ(x, y, R)

    # изменение объектов
    # ...

    # обновление экрана
    pg.display.update()
