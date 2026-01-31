# здесь подключаются модули:
import pygame as pg
import random
import time
import asyncio
# здесь определяются константы, функции и классы:
FPS = 60
WIDTH, HEIGHT = 1280, 900
WHITE = (255,255,255)
RED = (220, 50, 50)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)


class SpaceShip(pg.sprite.Sprite):
    def __init__(self):
        self.hp_max = 20
        self.hp = self.hp_max
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

class Planet(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(r'imagesgame/planet.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (220, 220))
        self.rect = self.image.get_rect()

        self.speed = 3
        self.rect.x = WIDTH + random.randint(200, 600)
        self.rect.y = random.randint(50, HEIGHT - self.rect.height - 50)

        self.drop_radius = 140
        self.delivered = False

    def move(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    def try_deliver(self, ship_rect):
        sx, sy = ship_rect.center
        px, py = self.rect.center
        dx = sx - px
        dy = sy - py
        in_zone = (dx*dx + dy*dy) <= (self.drop_radius * self.drop_radius)

        if in_zone and not self.delivered:
            self.delivered = True
            return True
        return False

class Asteroids(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        num = random.randint(1,5)
        asteroid_scale = random.randint(200, 400)
        self.image = pg.image. load(r'imagesgame/asteroid' + str(num) + '.png')
        self.image = pg.transform.scale(self.image, (asteroid_scale, asteroid_scale))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.speed = random.randint(5,10)
        self.x = WIDTH
        self.y = random.randint(0, HEIGHT - asteroid_scale)

    def move(self):
        self.x -= self.speed
        self.rect.topleft = (self.x, self.y)
        if self.rect.right < 0:
            self.kill()
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

def draw_ui(screen, money, deliveries):
    font = pg.font.Font(None, 48)

    money_text = font.render(f"Money: {money}$", True, WHITE)
    screen.blit(money_text, (WIDTH - 300, 20))

    deliveries_text = font.render(f"Deliveries: {deliveries}", True, WHITE)
    screen.blit(deliveries_text, (WIDTH - 300, 50))

def draw_hp(screen, hp, hp_max):
    font = pg.font.Font(None, 48)
    text = font.render("HP:", True, RED)
    screen.blit(text, (20, 20))

    size = 25
    a = 8
    start_x = 20 + text.get_width() + 15
    y = 25

    for i in range(hp_max):
        color = RED if i < hp else GRAY
        pg.draw.rect(screen, color, (start_x + i * (size + a), y, size, size), 0)
        pg.draw.rect(screen, BLACK, (start_x + i * (size + a), y, size, size), 2)

# здесь происходит инициализация:
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # здесь можно указать и другие настройки экрана (битовые флаги)
pg.display.set_caption("Игра")
clock = pg.time.Clock()
background = Background()
# здесь происходит создание игровых объектов:
# ...
font1 = pg.font.Font(None, 96)
asteroids = pg.sprite.Group()
spaceship = SpaceShip()
planets = pg.sprite.Group()
money = 0
deliveries = 0
cooldown = 0
font_ui = pg.font.Font(None, 36)
# если надо до игрового цикла (=на самом старте игры) отобразить объекты, то отрисовываем их здесь:
# ...
pg.display.update()  # затем обновляем экран, чтобы показать изменения
spawn_asteroid = pg.USEREVENT + 1
SPAWN_PLANET = pg.USEREVENT + 2
pg.time.set_timer(spawn_asteroid, 600)
pg.time.set_timer(SPAWN_PLANET, 3500)
# главный игровой цикл:
flag_play = True
while flag_play:
    clock.tick(FPS)  # настраиваем FPS (=частоту итераций в секунду)
    cooldown += 1

    # цикл обработки событий:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            flag_play = False
            break
        if event.type == spawn_asteroid:
            asteroids.add(Asteroids())
        if event.type == SPAWN_PLANET:
            planets.add(Planet())
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
    for asteroid in asteroids:
        asteroid.move()
    background.move()
    background.draw(screen)
    spaceship.draw(screen)
    planets.draw(screen)
    asteroids.draw(screen)
    draw_hp(screen, spaceship.hp, spaceship.hp_max)
    if pg.sprite.spritecollideany(spaceship, asteroids, collided=pg.sprite.collide_mask):
        if cooldown >= 30:
            # explosion(x,y)
            cooldown = 0
            spaceship.hp -= 1
        if spaceship.hp <= 0:
            break
    for planet in planets:
        planet.move()
        if planet.try_deliver(spaceship.rect):
            deliveries += 1
            salary = random.randint(20, 80)
            chance = random.randint(1,25)
            if chance == 20:
                salary += random.randint(200, 500)
                text = font1.render("Big Tips", True, WHITE)
                screen.blit(text, (300, 300))
            if chance > 20:
                salary += random.randint(20,50)
                text = font1.render("Tips", True, WHITE)
                screen.blit(text, (300, 300))
            money += salary
            # count of delivery and money
            pass
        draw_ui(screen, money, deliveries)
    pg.display.update()  # обновление экрана, чтобы отобразить новую перерисовку
