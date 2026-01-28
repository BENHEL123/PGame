# здесь подключаются модули:
import pygame as pg
import random
# здесь определяются константы, функции и классы:
FPS = 60
WIDTH, HEIGHT = 1280, 900
WHITE = (255,255,255)

class SpaceShip:
    def __init__(self):
        self.image = pg.image.load(r'imagesgame/spaceship.png')
        self.image = pg.transform.scale(self.image, (150, 150))
        self.image = pg.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.speed = 5

    def move(self, dy=0):
        if (self.rect.top + dy * self.speed) > 0 and (self.rect.bottom + dy * self.speed) < HEIGHT:
            self.rect.y += dy * self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Asteroids:
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        num = random.randint(1,5)
        asteroid_scale = random.randint(200, 500)
        self.image = pg.image. load(r'imagesgame/asteroid' + str(num) + '.png')
        self.image = pg.transform.scale(self.image, (asteroid_scale, asteroid_scale))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.speed = random.randint(5,15)
        self.x = WIDTH
        self.y = random.randint(0, HEIGHT - asteroid_scale)

    def move(self):
        self.x -= self.speed
        if self.rect.right < 0:
            self.remove(asteroids_group)
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Background:
    def __init__(self):
        self.image = pg.image.load(r'imagesgame/background.jpeg')
        self.speed = 3
        self.width = self.image.get_width()
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
        screen.blit(self.image, (self.x1, 0))
        screen.blit(self.image, (self.x2, 0))
        screen.blit(self.image, (self.x3, 0))

# здесь происходит инициализация:
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # здесь можно указать и другие настройки экрана (битовые флаги)
pg.display.set_caption("Игра")
clock = pg.time.Clock()
background = Background()
# здесь происходит создание игровых объектов:
# ...
asteroids = pg.sprite.Group()
spaceship = SpaceShip()
# если надо до игрового цикла (=на самом старте игры) отобразить объекты, то отрисовываем их здесь:
# ...
pg.display.update()  # затем обновляем экран, чтобы показать изменения
spawn_asteroid = pg.USEREVENT
pg.time.set_timer(spawn_asteroid, 1500)
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
        if event.type == spawn_asteroid:
            asteroids.add(Asteroids())
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
    if pg.sprite.spritecollideany(spaceship, asteroids, collided=pg.sprite.collide_mask) is not None:
        break
    pg.display.update()  # обновление экрана, чтобы отобразить новую перерисовку
