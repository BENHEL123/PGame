import pygame as pg

FPS = 60
W,H = 1400, 900

# цвета выбраны с сайта: https://htmlcolorcodes.com/
MINT = (181, 222, 149)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (238, 181, 50)
FIRE = (245, 112, 37)
DARK_BROWN = (110, 7, 7)
BROWN = (166, 13, 13)
GREEN = (0, 204, 102)
BLUE = (0, 128, 255)
LIGHT_BLUE = (21, 219, 219)
DARK_GREEN = (0, 102, 0)

pg.init()
screen = pg.display.set_mode((W, H))
screen.fill(BLUE)  # заливка фона
pg.display.set_caption("Игра")
clock = pg.time.Clock()

pg.draw.rect(screen, BROWN, (250, 300, 700, 400))
pg.draw.rect(screen, GREEN, (0, 700, 1400, 900))
pg.draw.rect(screen, DARK_BROWN, (1175, 650, 50, 50))
h1, h2 = 650, 550
w1, w3 = 1100, 1300
for i in range(3):
    pg.draw.polygon(screen, DARK_GREEN, [[w1, h1], [1200, h2], [w3, h1]])
    h1 -= 80
    h2 -= 80
    w1 += 25
    w3 -= 25

pg.draw.polygon(screen, BROWN, [[250, 300], [950, 300], [600, 100]])

def log(x1, y1):
    pg.draw.circle(screen, BROWN, (x1, y1),29)
    pg.draw.circle(screen, DARK_BROWN, (x1, y1), 30, 5)
    pg.draw.circle(screen, DARK_BROWN, (x1, y1), 25, 2)
    pg.draw.circle(screen, DARK_BROWN, (x1, y1), 20, 2)
    pg.draw.circle(screen, DARK_BROWN, (x1, y1), 15, 2)

y1 = 300
for i in range(17):
    pg.draw.line(screen, DARK_BROWN, (250, y1), (950, y1), 4)
    y1 += 25


x1, y1 = 250, 300
for i in range(8):
    log(x1, y1)
    y1+= 55
x1, y1 = 950, 300
for i in range(8):
    log(x1, y1)
    y1 += 55

pg.draw.ellipse(screen, DARK_BROWN, (540, 390, 120, 220))
pg.draw.ellipse(screen, LIGHT_BLUE, (550, 400, 100, 200))
pg.draw.line(screen, DARK_BROWN, (650, 450), (800, 450))

# отображаем нарисованные объекты
pg.display.update()

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

    pg.display.update()
