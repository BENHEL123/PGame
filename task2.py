import pygame as pg

FPS = 60
WIN_WIDTH = 400
WIN_HEIGHT = 100
WHITE = (255, 255, 255)
ORANGE = (255, 150, 100)
CNT = 2
SPEED = 2

pg.init()
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
screen.fill(WHITE)  # белый фон
pg.display.set_caption("Игра")
clock = pg.time.Clock()

# до начала игрового цикла отображаем объекты:
r = 30  # радиус круга
# координаты центра круга:
x = 0 + r # скрываем за левой границей
y = WIN_HEIGHT // 2  # выравниваем по центру по вертикали
pg.draw.polygon(screen, ORANGE,
                [[x - r, y - r], [x + r, y - r], [x + r, y + r], [x - r, y + r]])  # рисуем круг
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

    # изменение состояний объектов:
    # если круг полностью скрылся за правой границей
    if x >= WIN_WIDTH - r:
        SPEED = SPEED / -1
        SPEED -= 2
        x += SPEED
    elif x <= 0 + r:
        SPEED = SPEED / -1
        SPEED += 2
        x += SPEED
    else:  # если еще нет
        x += SPEED # то на следующей итерации цикла круг отобразится немного правее

    screen.fill(WHITE)  # заливаем фон, стирая предыдущий круг
    pg.draw.polygon(screen, ORANGE,
                    [[x - r, y - r], [x + r, y - r], [x + r, y + r], [x - r, y + r]])  # рисуем круг

    pg.display.update()  # обновляем окно
