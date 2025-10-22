# здесь подключаются модули:
import pygame as pg

def move_ball(x1, y1, SPEED1):
    x, y, SPEED = x1, y1, SPEED1
    if x >= WIDTH and y == H1:
        x, y = WIDTH, H2
    if x <= 0 - BALL_WIDTH and y == H2:
        x, y = 0 - BALL_WIDTH, H1
    if 0 - BALL_WIDTH <= x <= WIDTH + BALL_WIDTH and y <= 150:
        x += SPEED
    if 0 - BALL_WIDTH <= x <= WIDTH + BALL_WIDTH and y >= 300:
        x -= SPEED
    return(x, y)

# здесь определяются константы, функции и классы:
FPS = 60
WIDTH, HEIGHT = 1000, 600
LIGHT_BLUE_BLUE = (96, 110, 140)
LIGHT_PURPLE = (108, 77, 117)
BLUE = (0, 51, 153)
WHITE = (255, 255, 255)
R = 50
BALL_WIDTH = 100
BALL_HEIGTH = 100
H1 = HEIGHT / 6 + 15
H2 = HEIGHT / 6 + 275 + 15
SPEED = 5

# здесь происходит инициализация:
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # здесь можно указать и другие настройки экрана (битовые флаги)
pg.display.set_caption("Игра")

clock = pg.time.Clock()

# здесь происходит создание игровых объектов:
# ...
background = pg.Surface((WIDTH, HEIGHT))
background.fill(LIGHT_PURPLE)
pg.draw.rect(background, LIGHT_BLUE_BLUE, (0, HEIGHT / 6, WIDTH, 130))
pg.draw.rect(background, LIGHT_BLUE_BLUE, (0, HEIGHT / 6 + 275, WIDTH, 130))


ball = pg.Surface((BALL_WIDTH, BALL_HEIGTH), pg.SRCALPHA)
ball.fill((0, 0, 0, 0))
pg.draw.circle(ball, (*BLUE, 90), (BALL_WIDTH / 2, BALL_HEIGTH / 2), R)
# если надо до игрового цикла (=на самом старте игры) отобразить объекты, то отрисовываем их здесь:

x1, y1 = 1000, H2
x, y = 0, H1
screen.blit(background, (0, 0))
screen.blit(ball, (x, y))

pg.display.update()  # затем обновляем экран, чтобы показать изменения

# главный игровой цикл:
flag_play = True
while flag_play:
    clock.tick(FPS)  # настраиваем FPS (=частоту итераций в секунду)

    # цикл обработки событий:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            flag_play = False
            break
    if not flag_play:
        break
    # if x >= WIDTH and y == H1:
    #     x, y = WIDTH, H2
    # if x <= 0 - BALL_WIDTH and y == H2:
    #     x, y = 0 - BALL_WIDTH, H1
    # if 0 - BALL_WIDTH <= x <= WIDTH + BALL_WIDTH and y <= 150:
    #     x += SPEED
    # if 0 - BALL_WIDTH <= x <= WIDTH + BALL_WIDTH and y >= 300:
    #     x -= SPEED
    #
    # if x1 >= WIDTH and y1 == H1:
    #     x1, y1 = WIDTH, H2
    # if x1 <= 0 - BALL_WIDTH and y1 == H2:
    #     x1, y1 = 0 - BALL_WIDTH, H1
    # if 0 - BALL_WIDTH <= x1 <= WIDTH + BALL_WIDTH and y1 <= 150:
    #     x1 += SPEED + 5
    # if 0 - BALL_WIDTH <= x1 <= WIDTH + BALL_WIDTH and y1 >= 300:
    #     x1 -= SPEED + 5
    x, y = move_ball(x, y, SPEED)
    x1, y1 = move_ball(x1, y1, SPEED + 5)
    screen.blit(background, (0, 0))


    # изменение характеристик объектов:
    # ...

    # перерисовка экрана:
    # ...
    screen.blit(background, (0, 0))
    screen.blit(ball, (x, y))
    screen.blit(ball, (x1, y1))
    pg.display.update()  # обновление экрана, чтобы отобразить новую перерисовку
