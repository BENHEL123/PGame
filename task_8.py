import pygame as pg
import random
import time

FPS = 60
WIDTH, HEIGHT = 1000, 600
LIGHT_BLUE_BLUE = (96, 110, 140)
LIGHT_PURPLE = (108, 77, 117)
BLUE = (0, 51, 153)
R = 50
BALL_WIDTH = BALL_HEIGTH = R * 2
H1 = HEIGHT / 6 + 15
H2 = HEIGHT / 6 + 275 + 15


class Ball:
    def __init__(self):
        self.ball_surf = pg.Surface((BALL_WIDTH, BALL_HEIGTH), pg.SRCALPHA)
        self.ball_rect = self.ball_surf.get_rect(topleft=(0 - R, H1))
        self.ball_surf.fill((0, 0, 0, 0))
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.color = (r, g, b)
        pg.draw.circle(self.ball_surf, (*self.color, 90), (BALL_WIDTH // 2, BALL_HEIGTH // 2), R)
        self.speed = random.randint(5, 15)

    def move_ball(self):
        if self.ball_rect.left >= WIDTH and self.ball_rect.top == H1:
            self.ball_rect.top = H2
            self.ball_rect.left = WIDTH
        if self.ball_rect.right <= 0 and self.ball_rect.top == H2:
            self.ball_rect.top = H1
            self.ball_rect.left = 0 - BALL_WIDTH
        if 0 - BALL_WIDTH <= self.ball_rect.left <= WIDTH + BALL_WIDTH and self.ball_rect.top <= 150:
            self.ball_rect.move_ip(self.speed, 0)
        if 0 - BALL_WIDTH <= self.ball_rect.left <= WIDTH + BALL_WIDTH and self.ball_rect.top >= 300:
            self.ball_rect.move_ip(-self.speed, 0)

    def draw(self, screen):
        screen.blit(self.ball_surf, self.ball_rect)


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Игра")
clock = pg.time.Clock()

background = pg.Surface((WIDTH, HEIGHT))
background.fill(LIGHT_PURPLE)
pg.draw.rect(background, LIGHT_BLUE_BLUE, (0, HEIGHT / 6, WIDTH, 130))
pg.draw.rect(background, LIGHT_BLUE_BLUE, (0, HEIGHT / 6 + 275, WIDTH, 130))

balls = [Ball(), Ball()]

screen.blit(background, (0, 0))
for oneball in balls:
    oneball.draw(screen)
pg.display.update()
cnt = 0
flag_play = True
while flag_play:
    clock.tick(FPS)
    cnt += 1
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            flag_play = False
            break
    if not flag_play:
        break

    for oneball in balls:
        oneball.move_ball()
    keys = pg.key.get_pressed()
    if keys[pg.K_SPACE] and cnt >= 15:
        cnt = 0
        balls.append(Ball())
    screen.blit(background, (0, 0))
    for oneball in balls:
        oneball.draw(screen)
    pg.display.update()
