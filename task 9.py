import pygame as pg
import random

# здесь определяются константы, функции и классы:
FPS = 60
WIDTH, HEIGHT = 1000, 600
YELLOW = (255, 255, 0)
ORANGE = (252, 102, 0)
White = (255, 255, 255)
BLACK = (0, 0, 0)

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
        self.r = 15
        old_center = self.rect.center
        self.surf = pg.Surface((self.r * 2, self.r * 2), pg.SRCALPHA)
        self.rect = self.surf.get_rect(center=old_center)
        self.surf.fill((0, 0, 0, 0))
        pg.draw.circle(self.surf, (*ORANGE, 255), (self.rect.width // 2, self.rect.width // 2), self.r)
        self.mask = pg.mask.from_surface(self.surf)

    def get_r(self):
        return self.r

    def get_coord(self, a):
        if a == 0:
            x = self.rect.left
            x1 = self.rect.right
            return x, x1
        elif a == 1:
            x = self.rect.bottom
            x1 = self.rect.top
            return x, x1

class Button:
    def __init__(self, text, text_size, text_color, button_color, button_cover_color, button_pos):
        self.button_color = button_color
        self.button_cover_color = button_cover_color
        self.font = pg.font.SysFont(None, text_size)
        # поверхность и Rect текста:
        self.text_surf = self.font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=button_pos)
        # т. к. она прилегает к тексту вплотную, делаем поверхность и Rect кнопки, границы к-рой будут на 50px дальше:
        self.button_surf = pg.Surface((self.text_surf.get_width() + 50, self.text_surf.get_height() + 50))
        self.button_rect = self.button_surf.get_rect(center=button_pos)
        self.button_surf.fill(button_color)
        pg.draw.rect(self.button_surf, BLACK, (0, 0, self.button_rect.width, self.button_rect.height), 3)

    def redraw(self, state):  # state = True, если курсор на кнопке; state = False, если курсор вне кнопки
        if state:
            self.button_surf.fill(self.button_cover_color)
            pg.draw.rect(self.button_surf, BLACK, (0, 0, self.button_rect.width, self.button_rect.height), 3)
        else:
            self.button_surf.fill(self.button_color)
            pg.draw.rect(self.button_surf, BLACK, (0, 0, self.button_rect.width, self.button_rect.height), 3)

    def draw(self, screen):
        screen.blit(self.button_surf, self.button_rect)
        screen.blit(self.text_surf, self.text_rect)


def check_click_on_button(button):
    global worm
    if button.button_rect.collidepoint(pg.mouse.get_pos()):
        worm.reset()

class Text:
    def __init__(self, text, text_size, text_color, text_pos):
        self.font = pg.font.SysFont(None, text_size)  # пусть будет стандартный шрифт pygame для всех текстов
        self.surf = self.font.render(text, True, text_color)  # пусть все тексты будут сглажены и без фона
        self.rect = self.surf.get_rect(topleft=text_pos)

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

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
button = Button('reset', 50, White, ORANGE, BLACK, (WIDTH / 2, HEIGHT * 5/6))
text = Text(f"current size:{worm.get_r()}", 50, ORANGE, (50,50))

button.draw(screen)
text.draw(screen)
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
        elif event.type == pg.MOUSEBUTTONDOWN:
            check_click_on_button(button)
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
    if worm.get_coord(0)[0] < 0:
        worm.move(dx=1)
    if worm.get_coord(0)[1] > WIDTH:
        worm.move(dx=-1)
    if worm.get_coord(1)[1] > HEIGHT:
        worm.move(dy=-1)
    if worm.get_coord(1)[0] < 0:
        worm.move(dy=1)
    cnt = 0



    if len(foods) < 4:
        foods.append(Food())
    check_hitbox()

    # изменение характеристик объектов:
    # ...

    # перерисовка экрана:
    # ...
    Button('reset', 50, White, ORANGE, BLACK, (WIDTH / 2, HEIGHT * 5/6))
    screen.blit(background, (0, 0))
    for food in foods:
        food.draw(screen)
    worm.draw(screen)
    button.draw(screen)
    text = Text(f"current size:{worm.get_r()}", 50, ORANGE, (50, 50))
    text.draw(screen)
    pg.display.update()  # затем обновляем экран, чтобы показать изменения
