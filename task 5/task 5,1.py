#TASK 4.1
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
    x = random.randint(R, WIDTH - R)
    y = random.randint(R, HEIGHT - R)
    pg.draw.circle(screen, ORANGE, (x, y), R)
# если надо до цикла отобразить какие-то объекты, обновляем экран
circ()
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
    if 
    # изменение объектов
    # ...



    # обновление экрана
    pg.display.update()
