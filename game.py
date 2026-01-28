# здесь подключаются модули:
import pygame as pg
import random
import random
# здесь определяются константы, функции и классы:
FPS = 60
WIDTH, HEIGHT = 1280, 900
WHITE = (255,255,255)

class SpaceShip:
    def __init__(self):
        self.surf = pg.image.load(r'imagesgame/spaceship.jpeg')
        self.surf = pg.transform.scale(self.surf, (150, 150))
        self.surf = pg.transform.rotate(self.surf, 90)
        self.rect = self.surf.get_rect()
        self.mask = pg.mask.from_surface(self.surf)
        self.speed = 5

    def move(self, dy=0):
        if (self.rect.top + dy * self.speed) > 0 and (self.rect.bottom + dy * self.speed) < HEIGHT:
            self.rect.y += dy * self.speed

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

class Asteroids:
    def __init__(self):
        num = random.randint(1,5)
        asteroid_scale = random.randint(200, 500)
        self.surf = pg.image. load(r'imagesgame/asteroid' + str(num) + '.jpeg')
        self.surf = pg.transform.scale(self.surf, (asteroid_scale, asteroid_scale))
        self.rect = self.surf.get_rect()
        self.mask = pg.mask.from_surface(self.surf)
        self.speed = random.randint(5,15)
        self.x = WIDTH

    def move(self):
        self.x -= 3

    def draw(self, screen):
        screen.blit(self.surf, (self.x, self.random_y))

class Background:
    def __init__(self):
        self.surf = pg.image.load(r'imagesgame/background.jpeg')
        self.speed = 3
        self.width = self.surf.get_width()
        self.x1 = 0
        self.x2 = self.width
        self.x3 = self.width * 2

    def move(self):
        self.x1 -= self.speed
        self.x2 -= self.speed
        self.x3 -= self.speed
        if self.x1 <= -self.width:
            self.x1 = self.x3 + self.width
        if self.x2 <= -self.width:
            self.x2 = self.x1 + self.width
        if self.x3 <= -self.width:
            self.x3 = self.x2 + self.width

    def draw(self, screen):
        screen.blit(self.surf, (self.x1, 0))
        screen.blit(self.surf, (self.x2, 0))
        screen.blit(self.surf, (self.x3, 0))

# здесь происходит инициализация:
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # здесь можно указать и другие настройки экрана (битовые флаги)
pg.display.set_caption("Игра")
clock = pg.time.Clock()
background = Background()
# здесь происходит создание игровых объектов:
# ...
asteroids = Asteroids()
spaceship = SpaceShip()
# если надо до игрового цикла (=на самом старте игры) отобразить объекты, то отрисовываем их здесь:
# ...
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

    keys = pg.key.get_pressed()
    if keys[pg.K_UP]:
        spaceship.move(dy=-1)
    if keys[pg.K_DOWN]:
        spaceship.move(dy=1)
    screen.fill(WHITE)


    # изменение характеристик объектов:
    # ...

    # перерисовка экрана:
    # ...
    background.move()
    background.draw(screen)
    spaceship.draw(screen)
    asteroids.draw(screen)
    pg.display.update()  # обновление экрана, чтобы отобразить новую перерисовку
