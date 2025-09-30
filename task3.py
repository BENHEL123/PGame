# здесь подключаются модули
import pygame as pg

# здесь определяются константы, функции и классы
FPS = 60
WIDTH = 1000
HEIGHT = 600
WHITE = (255,255,255)
# здесь происходит инициализация, создание объектов
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # также здесь можно указать битовые флаги
pg.display.set_caption("Игра")
clock = pg.time.Clock()

r_x = 100
r_y = 75
x = 0
y = 0
flag_x = True
flag_y = False
rflag_x = False
rflag_y = False
pg.draw.ellipse(screen, WHITE, (x,y,r_x,r_y))
# если надо до цикла отобразить какие-то объекты, обновляем экран
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

    # изменение объектов
if x == WIDTH and y == 0:
    flag_x = False
    rflag_y = True
elif x == WIDTH and y == HEIGHT:
    rflag_y = False
    rflag_x = True
elif x == 0 and y == HEIGHT:
    rflag_x = False
    rflag_y = True
elif x == 0 and y == 0:
    rflag_y = False
    flag_x = True

if flag_y:
    y += 2
elif flag_x:
    x += 2
elif rflag_x:
    x -= 2
elif rflag_y:
    y -= 2



    screen.fill()
    pg.draw.ellipse(x,y,r_x,r_y)
    pg.display.update()
