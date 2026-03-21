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

STATE1 = "FLY"
STATE2 = "SHOP"
STATE3 = "ENTER"
STATE4 = "ROUTE"
STATE5 = "CARGO"


class SpaceShip(pg.sprite.Sprite):
    def __init__(self, size=(150,150), angle=90):
        self.hp_max = 20
        self.hp = self.hp_max
        self.image = pg.image.load(r'imagesgame/spaceship.png').convert_alpha()
        self.image = pg.transform.scale(self.image, size)
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.speed = 5

    def move(self, dy=0):
        current_speed = max(2, self.speed - cargo_weight)
        if (self.rect.top + dy * current_speed) > 0 and (self.rect.bottom + dy * current_speed) < HEIGHT:
            self.rect.y += dy * current_speed

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


class StationPlanet(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(r'imagesgame/planet.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (750, 750))

        self.rect = self.image.get_rect()
        self.speed = 2
        self.rect.x = WIDTH + 100
        self.rect.y = 75

    def move(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class CargoOffer:
    def __init__(self, name, reward, weight, color):
        self.name = name
        self.reward = reward
        self.weight = weight
        self.color = color

def generate_cargo():
    pool = [
        CargoOffer("Food", 80, 0, (120, 220, 120)),
        CargoOffer("Parts", 130, 1, (180, 180, 180)),
        CargoOffer("Medicine", 170, 1, (120, 180, 255)),
        CargoOffer("Gold", 300, 2, (255, 215, 0)),
        CargoOffer("Crystals", 360, 2, (120, 255, 255)),
        CargoOffer("Artifact", 500, 3, (220, 120, 255)),
    ]
    return random.sample(pool, 3)

class Bullet(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((15,5))   # pg.image.load(r'imagesgame/bullet.png').convert.alpha()
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.speed = 15

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > WIDTH:
            self.kill()

class Asteroids(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        num = random.randint(1,5)
        asteroid_scale = random.randint(200, 400)
        self.image = pg.image.load(r'imagesgame/asteroid' + str(num) + '.png').convert_alpha()
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
        self.orig_speed = self.speed
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

class ShopPanel:
    def __init__(self, y_pos, title, price, description):
        self.font_title = pg.font.Font(None, 42)
        self.font_description= pg.font.Font(None, 32)
        self.width = 500
        self.height = 110

        # Позиция
        self.target_x = WIDTH - self.width - 50
        self.current_x = WIDTH
        self.y = y_pos


        self.title = title
        self.price = price
        self.description = description


        self.rect = pg.Rect(self.current_x, self.y, self.width, self.height)
        self.buy_button_rect = pg.Rect(0, 0, 120, 40) # Кнопка buy

    def update(self):
        self.current_x += (self.target_x - self.current_x) * 0.08
        self.rect.x = int(self.current_x)

        self.buy_button_rect.center = (self.rect.right - 80, self.rect.centery + 25)

    def draw(self, screen, money):
        pg.draw.rect(screen, (20, 20, 40), self.rect, 5, 15)
        pg.draw.rect(screen, (100, 100, 200), self.rect, 2, 15)

        # text
        title_surf = self.font_title.render(f"{self.title} ({self.price}$)", True, WHITE)
        screen.blit(title_surf, (self.rect.x + 20, self.rect.y + 15))

        desc_surf = self.font_description.render(self.description, True, GRAY)
        screen.blit(desc_surf, (self.rect.x + 20, self.rect.y + 55))

        can_buy = money >= self.price
        btn_color = (40, 180, 40) if can_buy else (150, 40, 40)
        pg.draw.rect(screen, btn_color, self.buy_button_rect, 0, 8)
        buy_text = self.font_title.render("Buy", True, WHITE)
        screen.blit(buy_text, (self.buy_button_rect.centerx - buy_text.get_width() // 2, self.buy_button_rect.centery - buy_text.get_height() // 2))

def exit_btn(screen, rect, text, font):
    pg.draw.rect(screen, (0,204,204), rect, 0, 15)
    pg.draw.rect(screen, (0, 153, 153), rect, 2, 15)

    txt = font.render(text, True, (255, 255, 255))
    rect1 = txt.get_rect()
    screen.blit(txt, (rect.centerx - rect1.width // 2,
                      rect.centery - rect1.height // 2))

def draw_route_menu(screen, font_big, font_small, left_rect, right_rect):
    title = font_big.render("Choose planet", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    pg.draw.ellipse(screen, (80, 170, 255), left_rect)
    pg.draw.ellipse(screen, (183, 126, 61), right_rect)
    pg.draw.line(screen, (255, 0, 0), (800, 250), (1000, 500), 5)
    pg.draw.line(screen, (255, 0, 0),(1000, 250),(800, 500), 5)

    txt1 = font_small.render("Station", True, WHITE)
    txt2 = font_small.render("Cargo Terminal", True, WHITE)
    txt3 = font_small.render("Not Working Yet", True, WHITE)

    screen.blit(txt1, (left_rect.centerx - txt1.get_width() // 2, left_rect.bottom + 20))
    screen.blit(txt2, (right_rect.centerx - txt2.get_width() // 2, right_rect.bottom + 20))
    screen.blit(txt3, (right_rect.centerx - txt2.get_width() // 2, right_rect.bottom - 250))

def draw_cargo_menu(screen, font_big, font_small, cards, offers, back_btn):
    title = font_big.render("Cargo Terminal", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    for rect, cargo in zip(cards, offers):
        pg.draw.rect(screen, (30, 30, 60), rect, 0, 16)
        pg.draw.rect(screen, cargo.color, rect, 3, 16)

        name = font_small.render(cargo.name, True, WHITE)
        reward = font_small.render(f"Reward: {cargo.reward}$", True, WHITE)
        weight = font_small.render(f"Weight: {cargo.weight}", True, WHITE)

        screen.blit(name, (rect.x + 20, rect.y + 20))
        screen.blit(reward, (rect.x + 20, rect.y + 60))
        screen.blit(weight, (rect.x + 20, rect.y + 95))

    exit_btn(screen, back_btn, "Back", font_small)

def draw_station_menu(screen, font_big, font_small):
    title = font_big.render("Station", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    exit_btn(screen, station_btn_repair, "Repair - 100$", font_small)
    exit_btn(screen, station_btn_ammo, "Ammo +20 - 50$", font_small)
    exit_btn(screen, station_btn_engine, "Engine +2 - 200$", font_small)
    exit_btn(screen, station_btn_back, "Back", font_small)

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
font1 = pg.font.Font(None, 96)
asteroids = pg.sprite.Group()
spaceship = SpaceShip()

spaceship_shop = SpaceShip(size=(700, 700), angle=180)
planets = pg.sprite.Group()
bullets = pg.sprite.Group()
stations = pg.sprite.Group()
ammo = 20
money = 5000
deliveries = 0
damage_cooldown = 0
background.orig_speed = background.speed
shop_panels = [
    ShopPanel(200, 'Ammo Pack', 50, '+20 ammos'),
    ShopPanel(340, 'Engine Boost', 200, 'increase speed'),
    ShopPanel(480, 'Repair', 100, 'Restore ur hp')
]
state = STATE4  # fly - лететь; shop - остановка, магазин; ENTER - Вход в магазин
msg_timer = 0
btn_repair = pg.Rect(WIDTH//2 - 200, 350,   400, 60)
btn_speed = pg.Rect(WIDTH//2 - 200, 450, 400, 60)
btn_exit = pg.Rect(WIDTH//2 + 100, 700, 500, 100)
font_ui = pg.font.Font(None, 36)
#Cargo - выбор груза
cargo_offers = generate_cargo
selected_cargo = None
cargo_reward = 0
cargo_weight = 0
route_left_rect = pg.Rect(250, 260, 220, 220)
route_right_rect = pg.Rect(780, 260, 220, 220)
cargo_cards = [
    pg.Rect(170, 220, 300, 140),
    pg.Rect(490, 220, 300, 140),
    pg.Rect(810, 220, 300, 140)
]
btn_back_route = pg.Rect(WIDTH//2 - 120, 700, 240, 60)
station_btn_repair = pg.Rect(WIDTH//2 - 200, 260, 400, 60)
station_btn_ammo = pg.Rect(WIDTH//2 - 200, 360, 400, 60)
station_btn_engine = pg.Rect(WIDTH//2 - 200, 460, 400, 60)
station_btn_back = pg.Rect(WIDTH//2 - 200, 560, 400, 60)
transition_timer = 0
# если надо до игрового цикла (=на самом старте игры) отобразить объекты, то отрисовываем их здесь:
# ...
pg.display.update()  # затем обновляем экран, чтобы показать изменения
spawn_asteroid = pg.USEREVENT + 1
SPAWN_PLANET = pg.USEREVENT + 2
# pg.time.set_timer(spawn_asteroid, 600)
# pg.time.set_timer(SPAWN_PLANET, 3500)

station_timer = 0
station_cooldown = random.randint(600, 1000)
planet_timer = 0
planet_cooldown = random.randint(140, 180)
asteroid_timer = 0
asteroid_cooldown = random.randint(20, 60)
# главный игровой цикл:
flag_play = True
while flag_play:
    clock.tick(FPS)  # настраиваем FPS (=частоту итераций в секунду)
    damage_cooldown += 1
    if state == STATE1:
        planet_timer += 1
        asteroid_timer += 1
        station_timer += 1
    if planet_timer >= planet_cooldown:
        planets.add(Planet())
        planet_timer = 0
        planet_cooldown = random.randint(140, 180)
    if asteroid_timer >= asteroid_cooldown:
        asteroids.add(Asteroids())
        asteroid_timer = 0
        asteroid_cooldown = random.randint(20, 60)
    if station_timer >= station_cooldown:
        stations.add(StationPlanet())
        station_timer = 0
        station_cooldown = random.randint(600, 1000)
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
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and ammo > 0:
                bullets.add(Bullet())
                ammo -= 1
            if event.key == pg.K_e and state == STATE1:
                for station in stations:
                    if spaceship.rect.colliderect(station.rect):
                        state = STATE3
                        transition_timer = 0
                        station.kill()
        if event.type == pg.MOUSEBUTTONDOWN and state == STATE4:
            mouse_pos = pg.mouse.get_pos()
            if route_left_rect.collidepoint(mouse_pos):
                state = STATE2
            elif route_right_rect.collidepoint(mouse_pos):
                cargo_offers = generate_cargo()
                state = STATE5
        if event.type == pg.MOUSEBUTTONDOWN and state == STATE5:
            mouse_pos = pg.mouse.get_pos()
            for rect, cargo in zip(cargo_cards, cargo_offers):
                if rect.collidepoint(mouse_pos):
                    selected_cargo = cargo
                    cargo_reward = cargo.reward
                    cargo_weight = cargo.weight
                    state = STATE1
                    background.speed = background.orig_speed
                    asteroid_timer = 0
                    planet_timer = 0
            if btn_back_route.collidepoint(mouse_pos):
                state = STATE4
        if event.type == pg.MOUSEBUTTONDOWN and state == STATE2:
            mouse_pos = pg.mouse.get_pos()
            if shop_panels[1].buy_button_rect.collidepoint(mouse_pos) and money >= shop_panels[1].price:
                money -= shop_panels[1].price
                spaceship.speed += 2
            elif shop_panels[0].buy_button_rect.collidepoint(mouse_pos) and money >= shop_panels[0].price:
                ammo += 20
                money -= shop_panels[0].price
            elif shop_panels[2].buy_button_rect.collidepoint(mouse_pos) and money >= shop_panels[2].price:
                spaceship.hp = spaceship.hp_max
                money -= shop_panels[2].price
            elif btn_exit.collidepoint(mouse_pos):
                state = STATE1
                background.speed = background.orig_speed

    if not flag_play:
        break





    # изменение характеристик объектов:
    # ...

    # перерисовка экрана:
    # ...

    # Отрисовка
    if state == STATE1:
        # move starship and background
        background.move()
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            spaceship.move(dy=-1)
        if keys[pg.K_DOWN]:
            spaceship.move(dy=1)

        for station in stations:
            station.move()
        for asteroid in asteroids:
            asteroid.move()
        for planet in planets:
            planet.move()
            if planet.try_deliver(spaceship.rect):
                deliveries += 1
                salary = random.randint(20, 80)
                chance = random.randint(1, 25)
                msg_timer = 90
                if chance == 20:
                    salary += random.randint(200, 500)
                    text = font1.render("Big Tips", True, WHITE)
                elif chance > 20:
                    salary += random.randint(20, 50)
                    text = font1.render("Tips", True, WHITE)
                else:
                    text = font1.render("Delivered!", True, WHITE)
                money += salary + cargo_reward
                cargo_reward = 0
                cargo_weight = 0
                selected_cargo = None


        # collisions
        if pg.sprite.spritecollideany(spaceship, asteroids, collided=pg.sprite.collide_mask):
            if damage_cooldown >= 30:
                damage_cooldown = 0
                spaceship.hp -= 1
            if spaceship.hp <= 0: break
        hits = pg.sprite.groupcollide(asteroids, bullets, True, True, collided=pg.sprite.collide_mask)
        for hit in hits:
            money += 5
    # отрисовка
    screen.fill(WHITE)




    if state == STATE1:
        background.draw(screen)
        for station in stations:
            station.draw(screen)
            if spaceship.rect.colliderect(station.rect):
                text1 = font1.render("Press 'E' to ENTER", True, WHITE)
                screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT - 150))
        planets.draw(screen)
        asteroids.draw(screen)
        spaceship.draw(screen)
        if msg_timer > 0:
            msg_timer -= 1
            screen.blit(text, (300, 300))

    elif state == STATE3:
        transition_timer += 1
        background.speed *= 0.97
        background.move()

        for asteroid in asteroids:
            asteroid.move()
        for planet in planets:
            planet.move()

        if spaceship.rect.bottom > -20:
            spaceship.rect.y -= 4

        if background.speed < 0.15:
            background.speed = 0

        background.draw(screen)
        planets.draw(screen)
        asteroids.draw(screen)
        spaceship.draw(screen)

        if spaceship.rect.bottom <= 0:
            spaceship.rect.y = HEIGHT // 2
            background.speed = background.orig_speed
            state = STATE4

    elif state == STATE2:
        background.draw(screen)
        exit_btn(screen, btn_exit, "Exit", font_ui)
        for panel in shop_panels:
            panel.draw(screen, money)
            panel.update()
            spaceship_shop.draw(screen)

    elif state == STATE4:
        screen.fill((10, 10, 30))
        draw_route_menu(screen, font1, font_ui, route_left_rect, route_right_rect)

    elif state == STATE5:
        screen.fill((12, 12, 35))
        draw_cargo_menu(screen, font1, font_ui, cargo_cards, cargo_offers, btn_back_route)

    elif state == STATE2:
        screen.fill((12, 12, 35))
        draw_station_menu(screen, font1, font_ui)

    # UI
    draw_hp(screen, spaceship.hp, spaceship.hp_max)
    draw_ui(screen, money, deliveries)
    pg.display.update()  # обновление экрана, чтобы отобразить новую перерисовку
