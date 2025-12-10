# здесь подключаются модули:
import pygame as pg

# здесь определяются константы, функции и классы:
FPS = 60
WIDTH, HEIGHT = 1000, 600
WHITE = (255, 255, 255)

class Car:
    def __init__(self):
        self.speed = 5
        self.orig_surf = pg.image.load(r'images\car.png').convert_alpha()
        self.surf = self.orig_surf
        self.rect = self.surf.get_rect(center=(WIDTH/2, HEIGHT/2))
        self.angle = 0
        self.old_angle = self.angle

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

    def rotate(self):
        if self.angle != self.old_angle:
            rotated = pg.transform.rotate(self.orig_surf, self.angle)
            self.surf = rotated
            self.rect = rotated.get_rect(center=self.rect.center)
            self.old_angle = self.angle

    def move(self, dx=0, dy=0):
        if (self.rect.left + dx * self.speed) > 0 and (self.rect.right + dx * self.speed) < WIDTH:
            self.rect.x += dx * self.speed
            if dx > 0:
                self.angle = 270
            elif dx < 0:
                self.angle = 90
        if (self.rect.top + dy * self.speed) > 0 and (self.rect.bottom + dy * self.speed) < HEIGHT:
            self.rect.y += dy * self.speed
            if dy > 0:
                self.angle = 180
            elif dy < 0:
                self.angle = 0


# здесь происходит инициализация:
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # здесь можно указать и другие настройки экрана (битовые флаги)
pg.display.set_caption("Игра")
clock = pg.time.Clock()

# здесь происходит создание игровых объектов:
# ...

# если надо до игрового цикла (=на самом старте игры) отобразить объекты, то отрисовываем их здесь:
car = Car()



screen.fill(WHITE)
car.draw(screen)
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
    if keys[pg.K_LEFT]:
        car.move(dx=-1)
    elif keys[pg.K_RIGHT]:
        car.move(dx=1)
    elif keys[pg.K_UP]:
        car.move(dy=-1)
    elif keys[pg.K_DOWN]:
        car.move(dy=1)

    # изменение характеристик объектов:
    # ...

    # перерисовка экрана:
    # ...
    screen.fill(WHITE)
    car.rotate()
    car.draw(screen)
    pg.display.update()  # обновление экрана, чтобы отобразить новую перерисовку
