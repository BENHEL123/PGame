import pygame as pg

FPS = 60
WIDTH, HEIGHT = 600, 500
MINT = (230, 254, 212)
ORANGE = (255, 150, 100)

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Игра")
clock = pg.time.Clock()

# до начала игрового цикла отображаем объекты:
# координаты центра круга
x, y = WIDTH / 2, HEIGHT / 2  # координаты центра круга
r = 30  # радиус круга
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

    screen.fill(MINT)  # заливаем фон, стирая предыдущий круг
    pg.draw.circle(screen, ORANGE, (x, y), r)  # рисуем новый, сдвинутый круг

    pg.display.update()  # обновляем окно
