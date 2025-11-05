import pygame as pg
def move_ball(ball_rect, SPEED):
    if ball_rect.left >= WIDTH and ball_rect.top == H1:
        ball_rect.top = H2
        ball_rect.left = WIDTH
    if ball_rect.right <= 0 and ball_rect.top == H2:
        ball_rect.top = H1
        ball_rect.left = 0 - BALL_WIDTH
    if 0 - BALL_WIDTH <= ball_rect.left <= WIDTH + BALL_WIDTH and ball_rect.top <= 150:
        ball_rect.move_ip(SPEED, 0)
    if 0 - BALL_WIDTH <= ball_rect.left <= WIDTH + BALL_WIDTH and ball_rect.top >= 300:
        ball_rect.move_ip(-SPEED, 0)
    return ball_rect

FPS = 60
WIDTH, HEIGHT = 1000, 600
LIGHT_BLUE_BLUE = (96, 110, 140)
LIGHT_PURPLE = (108, 77, 117)
BLUE = (0, 51, 153)
R = 50
BALL_WIDTH = 100
BALL_HEIGTH = 100
H1 = HEIGHT / 6 + 15
H2 = HEIGHT / 6 + 275 + 15
SPEED = 5

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Игра")
clock = pg.time.Clock()

background = pg.Surface((WIDTH, HEIGHT))
background.fill(LIGHT_PURPLE)
pg.draw.rect(background, LIGHT_BLUE_BLUE, (0, HEIGHT / 6, WIDTH, 130))
pg.draw.rect(background, LIGHT_BLUE_BLUE, (0, HEIGHT / 6 + 275, WIDTH, 130))

ball = pg.Surface((BALL_WIDTH, BALL_HEIGTH), pg.SRCALPHA)
ball.fill((0, 0, 0, 0))
pg.draw.circle(ball, (*BLUE, 90), (BALL_WIDTH // 2, BALL_HEIGTH // 2), R)

# создаем rect для мяча
ball_rect = ball.get_rect(topleft=(0 - R, H1))
ball2_rect = ball.get_rect(topleft=(0 - R, H2))

screen.blit(background, (0, 0))
screen.blit(ball, ball_rect.topleft)
screen.blit(ball, ball2_rect.topleft)
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

    ball_rect = move_ball(ball_rect, SPEED)
    ball2_rect = move_ball(ball2_rect, SPEED + 5)

    screen.blit(background, (0, 0))
    screen.blit(ball, ball_rect.topleft)
    screen.blit(ball, ball2_rect.topleft)
    pg.display.update()
