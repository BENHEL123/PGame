import pygame, random, math
import sys

pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Ship:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT // 2
        self.vy = 0
        self.speed = 6
        self.size = 25
        self.hp = 3
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.vy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.speed
        self.y = max(self.size, min(HEIGHT - self.size, self.y + self.vy))
    
    def draw(self, surface):
        # Треугольник корабля
        points = [(self.x, self.y), (self.x - self.size, self.y + self.size//2),
                  (self.x - self.size, self.y - self.size//2)]
        pygame.draw.polygon(surface, (0, 255, 255), points)
        # Движки
        pygame.draw.circle(surface, (255, 100, 0), (self.x - self.size - 5, self.y), 4)

class Asteroid:
    def __init__(self):
        self.x = WIDTH + random.randint(0, 100)
        self.y = random.randint(50, HEIGHT - 50)
        self.vx = random.uniform(-4, -2)
        self.size = random.randint(15, 40)
    
    def update(self):
        self.x += self.vx
    
    def draw(self, surface):
        pygame.draw.circle(surface, (80, 80, 80), (int(self.x), int(self.y)), self.size)
    
    def collides_with(self, ship):
        dist = math.hypot(self.x - ship.x, self.y - ship.y)
        return dist < self.size + ship.size

class Planet:
    def __init__(self):
        self.x = WIDTH + random.randint(200, 400)
        self.y = random.randint(100, HEIGHT - 100)
        self.radius = random.randint(60, 100)
        self.color = random.choice([(255, 100, 100), (100, 255, 100), (100, 100, 255)])
        self.drop_zone_radius = 40
        self.delivery_done = False
        self.anim_timer = 0
    
    def update(self):
        self.x -= 3
        if self.delivery_done:
            self.anim_timer += 1
    
    def draw(self, surface, ship):
        # Планета
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Зона доставки
        zone_dist = math.hypot(self.x - ship.x, self.y - ship.y)
        if zone_dist < self.drop_zone_radius and not self.delivery_done:
            self.delivery_done = True
            return True  # Доставка!
        
        if self.delivery_done:
            # Анимация доставки
            pulse = math.sin(self.anim_timer * 0.3) * 10 + 20
            pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), pulse, 4)
        
        return False
    
    def is_offscreen(self):
        return self.x < -200

class Shop:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 120
        self.visible = False
        self.selected_upgrade = 0
        self.upgrades = [
            {"name": "Скорость +20%", "price": 150, "effect": "speed"},
            {"name": "Щиты +1 HP", "price": 200, "effect": "hp"},
            {"name": "Размер -10%", "price": 100, "effect": "size"}
        ]
    
    def show(self):
        self.visible = True
    
    def draw(self, surface, money):
        if not self.visible:
            return
        
        # Станция магазина
        pygame.draw.circle(surface, (200, 200, 200), (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (150, 150, 150), (self.x, self.y), self.radius, 5)
        
        # Апгрейды
        font = pygame.font.Font(None, 36)
        for i, upgrade in enumerate(self.upgrades):
            color = (255, 255, 0) if i == self.selected_upgrade else (255, 255, 255)
            text = font.render(f"{upgrade['name']} ({upgrade['price']}$)", True, color)
            
            if money >= upgrade['price']:
                pygame.draw.rect(surface, color, (100 + i * 300, HEIGHT - 150, 250, 80))
            else:
                pygame.draw.rect(surface, (100, 100, 100), (100 + i * 300, HEIGHT - 150, 250, 80))
            
            surface.blit(text, (110 + i * 300, HEIGHT - 140))

class Game:
    def __init__(self):
        self.state = "FLYING"  # FLYING, TRANSITION, SHOP
        self.ship = Ship()
        self.planets = []
        self.asteroids = []
        self.money = 0
        self.deliveries = 0
        self.spawn_timer = 0
        self.transition_timer = 0
        self.shop = Shop()
        
        # Апгрейды
        self.speed_multiplier = 1.0
        self.extra_hp = 0
    
    def update(self):
        if self.state == "FLYING":
            self.update_flying()
        elif self.state == "TRANSITION":
            self.update_transition()
        elif self.state == "SHOP":
            self.update_shop()
    
    def update_flying(self):
        self.ship.speed = 6 * self.speed_multiplier
        
        # Спавн
        self.spawn_timer += 1
        if self.spawn_timer > 60:
            if random.random() < 0.7:
                self.asteroids.append(Asteroid())
            else:
                self.planets.append(Planet())
            self.spawn_timer = 0
        
        # Обновление
        for planet in self.planets[:]:
            if planet.update():
                self.deliveries += 1
                self.money += 50
            if planet.is_offscreen():
                self.planets.remove(planet)
        
        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.collides_with(self.ship):
                self.ship.hp -= 1
                self.asteroids.remove(asteroid)
            
            if asteroid.x < -100:
                self.asteroids.remove(asteroid)
        
        # Переход к магазину
        if self.deliveries % 5 == 0 and self.deliveries > 0:
            self.state = "TRANSITION"
            self.transition_timer = 180  # 3 секунды
    
    def update_transition(self):
        self.transition_timer -= 1
        if self.transition_timer <= 0:
            self.state = "SHOP"
            self.shop.show()
    
    def update_shop(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and pygame.time.get_ticks() % 200 < 100:
            self.shop.selected_upgrade = (self.shop.selected_upgrade - 1) % 3
        if keys[pygame.K_RIGHT] and pygame.time.get_ticks() % 200 < 100:
            self.shop.selected_upgrade = (self.shop.selected_upgrade + 1) % 3
        
        if keys[pygame.K_RETURN]:
            upgrade = self.shop.upgrades[self.shop.selected_upgrade]
            if self.money >= upgrade['price']:
                self.apply_upgrade(upgrade['effect'])
                self.money -= upgrade['price']
                self.state = "FLYING"
                self.deliveries = 0
    
    def apply_upgrade(self, effect):
        if effect == "speed":
            self.speed_multiplier += 0.2
        elif effect == "hp":
            self.extra_hp += 1
            self.ship.hp += 1
    
    def draw(self, surface):
        surface.fill((10, 10, 40))  # Космос
        
        # Звёзды
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 1)
        
        # Игрок
        self.ship.draw(surface)
        
        # Объекты
        for planet in self.planets:
            planet.draw(surface, self.ship)
        for asteroid in self.asteroids:
            asteroid.draw(surface)
        
        # Магазин
        self.shop.draw(surface, self.money)
        
        # UI
        font = pygame.font.Font(None, 48)
        money_text = font.render(f"${self.money}", True, (0, 255, 0))
        deliveries_text = font.render(f"Доставок: {self.deliveries}/5", True, (255, 255, 255))
        hp_text = font.render(f"HP: {self.ship.hp}", True, (255, 0, 0))
        
        surface.blit(money_text, (20, 20))
        surface.blit(deliveries_text, (20, 70))
        surface.blit(hp_text, (20, 120))
        
        state_text = ""
        if self.state == "TRANSITION":
            state_text = "Подлетаем к станции..."
        elif self.state == "SHOP":
            state_text = "WASD - движение, ←→ - выбор, ENTER - купить"
        
        if state_text:
            instruction = pygame.font.Font(None, 36).render(state_text, True, (255, 255, 0))
            surface.blit(instruction, (WIDTH//2 - 200, HEIGHT//2 + 100))

# Запуск
game = Game()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
