import pygame as pg
import random

# здесь определяются константы, функции и классы:
FPS = 60
WIDTH, HEIGHT = 1000, 600
YELLOW = (255, 255, 0)
ORANGE = (252, 102, 0)
White = (0, 0, 0)

class Food:
    def __init__(self):
        self.r = random.randint(5, 50)
        x, y = random.randint(self.r, WIDTH - self.r), random.randint(self.r, HEIGHT - self.r)
        self.food_surface = pg.Surface((WIDTH / 4, WIDTH / 4), pg.SRCALPHA)
        self.rect = self.food_surface.get_rect(center=(x, y))
        pg.draw.circle(self.food_surface, (*YELLOW, 255), (self.rect.width // 2, self.rect.width // 2), self.r)
        self.mask = pg.mask.from_surface(self.food_surface)

    def draw(self, screen):
        screen.blit(self.food_surface, self.rect)

    def get_r(self):
        return self.r

class Worm:
    def __init__(self):
        self.r = 15
        self.surf = pg.Surface((self.r * 2, self.r * 2), pg.SRCALPHA)
        self.rect = self.surf.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.surf.fill((0, 0, 0, 0))
        pg.draw.circle(self.surf, (*ORANGE, 255), (self.rect.width // 2, self.rect.width // 2), self.r)
        self.speed = 3
        self.mask = pg.mask.from_surface(self.surf)

    def move(self, dx=0, dy=0):
        if (self.rect.left + dx * self.speed) > 0 and (self.rect.right + dx * self.speed) < WIDTH:
            self.rect.x += dx * self.speed
        if (self.rect.top + dy * self.speed) > 0 and (self.rect.bottom + dy * self.speed) < HEIGHT:
            self.rect.y += dy * self.speed

    def grow(self, food_r):
        if self.r < 100:             # 125
            self.r += food_r
            self.surf.fill((0, 0, 0, 0))
            self.surf = pg.Surface((self.r * 2, self.r * 2), pg.SRCALPHA)
            self.rect = self.surf.get_rect(center=(self.rect.center))
            pg.draw.circle(self.surf, (*ORANGE, 255), (self.rect.width // 2, self.rect.width // 2), self.r)
            self.mask = pg.mask.from_surface(self.surf)


    def draw(self, screen):
        screen.blit(self.surf, self.rect)

    def reset(self):
        return

    def get_r(self):
        return



def check_hitbox():
    global worm, foods
    for food in foods:
        offset = (food.rect.x - worm.rect.x, food.rect.y - worm.rect.y)
        if worm.mask.overlap(food.mask, offset) is not None:
            foods.remove(food)
            worm.grow(food.get_r())



# здесь происходит инициализация:
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # здесь можно указать и другие настройки экрана (битовые флаги)
pg.display.set_caption("Игра")
clock = pg.time.Clock()

background = pg.Surface((WIDTH, HEIGHT))
background.fill(White)
worm = Worm()


screen.blit(background, (0, 0))
foods = [Food() for i in range(4)]
# for food in foods:
#     food.draw(screen)
worm.draw(screen)
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
    if keys[pg.K_LEFT]:
        worm.move(dx=-1)
    if keys[pg.K_RIGHT]:
        worm.move(dx=1)
    if keys[pg.K_UP]:
        worm.move(dy=-1)
    if keys[pg.K_DOWN]:
        worm.move(dy=1)

    cnt = 0

    if len(foods) < 4:
        foods.append(Food())
    check_hitbox()

    # изменение характеристик объектов:
    # ...

    # перерисовка экрана:
    # ...
    screen.blit(background, (0, 0))
    for food in foods:
        food.draw(screen)
    worm.draw(screen)
    pg.display.update()  # затем обновляем экран, чтобы показать изменения
