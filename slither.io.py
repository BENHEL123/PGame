import pygame
import random
import math
import sys

# --- КОНФИГУРАЦИЯ ---
WIDTH, HEIGHT = 1280, 720
WORLD_SIZE = 4000
BG_COLOR = (10, 10, 15)
GRID_COLOR = (30, 30, 40)
FPS = 60

# Геймплей
BASE_RADIUS = 10
SPEED_NORMAL = 4.0
SPEED_BOOST = 7.0
TURN_SPEED = 0.2
START_LENGTH = 20
BOOST_COST = 0.5

# Способность "Призрак"
ABILITY_DURATION = 180  # кадрах (3 секунды при 60 FPS)
ABILITY_COOLDOWN = 600  # 10 секунд

# Частицы
PARTICLE_COUNT_DEATH = 40

# Черные дыры
BLACK_HOLE_COUNT = 5
BLACK_HOLE_FORCE = 1.5
BLACK_HOLE_RADIUS = 80

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slither.io: NEON CHAOS (Press 'E' for Ghost Mode)")
clock = pygame.time.Clock()

# Шрифты
font_ui = pygame.font.SysFont("consolas", 20, bold=True)
font_big = pygame.font.SysFont("arial", 60, bold=True)

# --- УТИЛИТЫ ---
def get_neon_color():
    # Яркие "кислотные" цвета
    colors = [
        (0, 255, 255), (255, 0, 255), (255, 255, 0), 
        (50, 255, 50), (255, 50, 50), (100, 100, 255)
    ]
    return random.choice(colors)

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# --- КЛАССЫ ---

class Particle:
    """Частицы для эффектов взрыва и следа"""
    def __init__(self, x, y, color, speed_factor=1.0):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 4) * speed_factor
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 50)
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.05)

    def draw(self, surface, cam_x, cam_y):
        if self.life > 0 and self.size > 0:
            sx = self.x - cam_x
            sy = self.y - cam_y
            if -10 < sx < WIDTH+10 and -10 < sy < HEIGHT+10:
                # Прозрачность через surface с альфа-каналом
                s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
                alpha = int((self.life / 50) * 255)
                pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
                surface.blit(s, (sx - self.size, sy - self.size))

class BlackHole:
    """Затягивает еду и искривляет путь змей"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BLACK_HOLE_RADIUS
        self.angle = 0

    def update(self):
        self.angle -= 0.1 # Вращение анимации

    def pull(self, obj_x, obj_y, factor=1.0):
        # Возвращает вектор смещения (dx, dy)
        dx = self.x - obj_x
        dy = self.y - obj_y
        dist = math.hypot(dx, dy)
        
        if dist < self.radius * 4 and dist > 10:
            force = (BLACK_HOLE_FORCE * 1000) / (dist * dist) * factor
            force = min(force, 5.0) # Ограничение силы
            angle = math.atan2(dy, dx)
            return math.cos(angle) * force, math.sin(angle) * force
        return 0, 0

    def draw(self, surface, cam_x, cam_y):
        sx = self.x - cam_x
        sy = self.y - cam_y
        if -200 < sx < WIDTH+200 and -200 < sy < HEIGHT+200:
            # Аккреционный диск (вращается)
            for i in range(3):
                offset = (self.angle + i * 2) % (math.pi * 2)
                rx = self.radius + math.sin(offset) * 10
                pygame.draw.circle(surface, (30, 0, 30), (int(sx), int(sy)), int(rx), 2)
            
            # Горизонт событий
            pygame.draw.circle(surface, (0, 0, 0), (int(sx), int(sy)), int(self.radius * 0.6))
            pygame.draw.circle(surface, (100, 0, 100), (int(sx), int(sy)), int(self.radius * 0.6), 2)


class Food:
    def __init__(self, x, y, energy, color=None):
        self.x = x
        self.y = y
        self.energy = energy
        self.color = color if color else get_neon_color()
        self.radius = 3 + energy
        self.drift_x = random.uniform(-0.2, 0.2)
        self.drift_y = random.uniform(-0.2, 0.2)

    def update(self, black_holes):
        self.x += self.drift_x
        self.y += self.drift_y
        
        # Гравитация черных дыр
        for bh in black_holes:
            dx, dy = bh.pull(self.x, self.y, factor=2.0) # Еда легче, тянется сильнее
            self.x += dx
            self.y += dy
            # Если засосало
            if distance((self.x, self.y), (bh.x, bh.y)) < bh.radius * 0.5:
                self.x = random.randint(0, WORLD_SIZE) # Телепорт (респаун) в другое место
                self.y = random.randint(0, WORLD_SIZE)

        self.x = max(0, min(WORLD_SIZE, self.x))
        self.y = max(0, min(WORLD_SIZE, self.y))

    def draw(self, surface, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if -20 < sx < WIDTH+20 and -20 < sy < HEIGHT+20:
            # Glow эффект (светящийся ореол)
            gfx_surf = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(gfx_surf, (*self.color, 60), (int(self.radius*2), int(self.radius*2)), int(self.radius+4))
            pygame.draw.circle(gfx_surf, self.color, (int(self.radius*2), int(self.radius*2)), int(self.radius))
            surface.blit(gfx_surf, (sx - self.radius*2, sy - self.radius*2))


class Snake:
    def __init__(self, x, y, is_bot=False, name="Bot"):
        self.x = x
        self.y = y
        self.segments = [{'x': x, 'y': y} for _ in range(START_LENGTH)]
        self.angle = random.uniform(0, math.pi * 2)
        self.target_angle = self.angle
        self.length_float = float(START_LENGTH)
        self.radius = BASE_RADIUS
        self.color = get_neon_color()
        self.is_bot = is_bot
        self.name = name
        self.alive = True
        self.boosting = False
        
        # Способности
        self.ghost_timer = 0
        self.cooldown_timer = 0
        
        # ИИ
        self.ai_timer = 0

    def update(self, dt, snakes, foods, black_holes, particles):
        if not self.alive: return

        # 1. Управление и Способности
        if not self.is_bot:
            mx, my = pygame.mouse.get_pos()
            self.target_angle = math.atan2(my - HEIGHT/2, mx - WIDTH/2)
            
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed()
            
            # Буст
            self.boosting = (keys[pygame.K_SPACE] or mouse[0]) and self.length_float > 10
            
            # Активация "Призрака" (E)
            if keys[pygame.K_e] and self.cooldown_timer == 0:
                self.ghost_timer = ABILITY_DURATION
                self.cooldown_timer = ABILITY_COOLDOWN
        else:
            self.ai_logic(snakes, foods, black_holes)

        # Таймеры способности
        if self.ghost_timer > 0: self.ghost_timer -= 1
        if self.cooldown_timer > 0: self.cooldown_timer -= 1

        # 2. Физика движения
        # Поворот
        diff = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        self.angle += diff * TURN_SPEED
        self.angle %= 2 * math.pi

        # Скорость и гравитация
        speed = SPEED_BOOST if self.boosting else SPEED_NORMAL
        
        # Влияние черных дыр на змею
        grav_x, grav_y = 0, 0
        for bh in black_holes:
            gx, gy = bh.pull(self.x, self.y, factor=0.8)
            grav_x += gx
            grav_y += gy
            # Смерть в черной дыре
            if distance((self.x, self.y), (bh.x, bh.y)) < bh.radius * 0.4:
                self.die(foods, particles)
                return

        self.x += math.cos(self.angle) * speed + grav_x
        self.y += math.sin(self.angle) * speed + grav_y
        
        # Границы
        self.x = max(0, min(WORLD_SIZE, self.x))
        self.y = max(0, min(WORLD_SIZE, self.y))

        # 3. Обновление сегментов
        self.segments.insert(0, {'x': self.x, 'y': self.y})
        target_len = int(self.length_float)
        while len(self.segments) > target_len:
            self.segments.pop()
            
        # Подтяжка (IK)
        seg_dist = 6
        for i in range(1, len(self.segments)):
            prev = self.segments[i-1]
            curr = self.segments[i]
            dx, dy = curr['x'] - prev['x'], curr['y'] - prev['y']
            dist_val = math.hypot(dx, dy)
            if dist_val > 0:
                scale = seg_dist / dist_val
                curr['x'] = prev['x'] + dx * scale
                curr['y'] = prev['y'] + dy * scale

        # 4. Расход массы и эффекты
        if self.boosting:
            self.length_float -= BOOST_COST
            if random.random() < 0.3:
                # Партиклы из хвоста
                tail = self.segments[-1]
                particles.append(Particle(tail['x'], tail['y'], self.color))
                # Оставляем еду
                if random.random() < 0.1:
                    foods.append(Food(tail['x'], tail['y'], 1, self.color))
                    
        self.radius = min(25, BASE_RADIUS + self.length_float / 150)

    def ai_logic(self, snakes, foods, black_holes):
        self.ai_timer -= 1
        if self.ai_timer > 0: return
        
        self.ai_timer = random.randint(5, 15)
        
        # Уклонение от черных дыр
        for bh in black_holes:
            if distance((self.x, self.y), (bh.x, bh.y)) < 400:
                angle_away = math.atan2(self.y - bh.y, self.x - bh.x)
                self.target_angle = angle_away
                self.boosting = True
                return

        # Поиск еды
        nearest = None
        min_d = 500
        for f in random.sample(foods, min(len(foods), 30)):
            d = distance((self.x, self.y), (f.x, f.y))
            if d < min_d:
                min_d = d
                nearest = f
        
        if nearest:
            self.target_angle = math.atan2(nearest.y - self.y, nearest.x - self.x)
            self.boosting = False
        else:
            self.target_angle += random.uniform(-0.5, 0.5)

    def check_collision(self, other):
        # Если мы "Призрак" - мы неуязвимы
        if self.ghost_timer > 0: return False
        # Если враг "Призрак" - мы сквозь него проходим (не убиваемся)
        if other.ghost_timer > 0: return False
        
        head = self.segments[0]
        # Оптимизация
        if abs(head['x'] - other.x) > 200: return False

        start = 2 if self == other else 0
        for i in range(start, len(other.segments)):
            seg = other.segments[i]
            if distance((head['x'], head['y']), (seg['x'], seg['y'])) < self.radius + other.radius - 2:
                return True
        return False

    def die(self, foods, particles):
        self.alive = False
        # Взрыв частиц
        for _ in range(PARTICLE_COUNT_DEATH):
            cx = self.segments[0]['x'] + random.randint(-20, 20)
            cy = self.segments[0]['y'] + random.randint(-20, 20)
            particles.append(Particle(cx, cy, self.color, speed_factor=2.0))
            
        # Еда из тела
        step = 2
        for i in range(0, len(self.segments), step):
            s = self.segments[i]
            foods.append(Food(s['x'], s['y'], 3, self.color))

    def draw(self, surface, cam_x, cam_y):
        if not self.alive: return
        
        # Если способность активна - змея полупрозрачная и белая
        alpha = 100 if self.ghost_timer > 0 else 255
        draw_color = (200, 255, 255) if self.ghost_timer > 0 else self.color
        
        # Рисуем сегменты
        for i, seg in enumerate(reversed(self.segments)):
            sx = int(seg['x'] - cam_x)
            sy = int(seg['y'] - cam_y)
            
            if -30 < sx < WIDTH+30 and -30 < sy < HEIGHT+30:
                # Создаем поверхность для прозрачности если нужно
                if alpha < 255:
                    s = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*draw_color, alpha), (int(self.radius), int(self.radius)), int(self.radius))
                    surface.blit(s, (sx - self.radius, sy - self.radius))
                else:
                    pygame.draw.circle(surface, draw_color, (sx, sy), int(self.radius))
                    # Небольшой блик для объема
                    pygame.draw.circle(surface, (255, 255, 255), (sx - 3, sy - 3), int(self.radius * 0.3))

        # Голова и глаза
        head = self.segments[0]
        hx, hy = int(head['x'] - cam_x), int(head['y'] - cam_y)
        
        # Глаза
        eye_r = self.radius * 0.35
        offset_x = math.cos(self.angle - 0.6) * self.radius * 0.7
        offset_y = math.sin(self.angle - 0.6) * self.radius * 0.7
        
        pygame.draw.circle(surface, (255, 255, 255), (int(hx + offset_x), int(hy + offset_y)), int(eye_r))
        offset_x2 = math.cos(self.angle + 0.6) * self.radius * 0.7
        offset_y2 = math.sin(self.angle + 0.6) * self.radius * 0.7
        pygame.draw.circle(surface, (255, 255, 255), (int(hx + offset_x2), int(hy + offset_y2)), int(eye_r))
        
        # Имя и статус
        if not self.is_bot:
            label = "GHOST MODE" if self.ghost_timer > 0 else "YOU"
            col = (100, 255, 255) if self.ghost_timer > 0 else (255, 255, 255)
            txt = font_ui.render(label, True, col)
            surface.blit(txt, (hx - txt.get_width()//2, hy - self.radius - 25))
            
            # Полоска кулдауна
            if self.cooldown_timer > 0:
                ratio = self.cooldown_timer / ABILITY_COOLDOWN
                pygame.draw.rect(surface, (50, 50, 50), (hx - 20, hy - self.radius - 35, 40, 5))
                pygame.draw.rect(surface, (255, 100, 0), (hx - 20, hy - self.radius - 35, 40 * (1-ratio), 5))

# --- МЕЙН ЛУП ---

player = Snake(WORLD_SIZE//2, WORLD_SIZE//2)
bots = [Snake(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), is_bot=True) for _ in range(20)]
foods = [Food(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), random.randint(1, 5)) for _ in range(600)]
black_holes = [BlackHole(random.randint(200, WORLD_SIZE-200), random.randint(200, WORLD_SIZE-200)) for _ in range(BLACK_HOLE_COUNT)]
particles = []

running = True
game_over = False

while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Рестарт
                player = Snake(WORLD_SIZE//2, WORLD_SIZE//2)
                bots = [Snake(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), is_bot=True) for _ in range(20)]
                foods = [Food(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), random.randint(1, 5)) for _ in range(600)]
                game_over = False
            if event.key == pygame.K_ESCAPE: running = False

    if not game_over:
        # Обновление
        for bh in black_holes: bh.update()
        
        all_snakes = [player] + bots
        for s in all_snakes:
            s.update(dt, all_snakes, foods, black_holes, particles)
            
        # Столкновения
        for s1 in all_snakes:
            if not s1.alive: continue
            for s2 in all_snakes:
                if s1 != s2 and s2.alive:
                    if s1.check_collision(s2):
                        s1.die(foods, particles)
                        if s1 == player: game_over = True

        # Поедание
        for s in all_snakes:
            if not s.alive: continue
            head = s.segments[0]
            # Быстрая проверка дистанции
            for f in foods[:]:
                if abs(head['x'] - f.x) < 40 and abs(head['y'] - f.y) < 40: # грубый бокс
                    if distance((head['x'], head['y']), (f.x, f.y)) < s.radius + f.radius:
                        s.length_float += f.energy
                        foods.remove(f)

        # Еда и частицы
        for f in foods: f.update(black_holes)
        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)
            
        # Респаун еды
        if len(foods) < 600:
            foods.append(Food(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), random.randint(1, 5)))
            
        # Респаун ботов
        bots = [b for b in bots if b.alive]
        if len(bots) < 15:
            bots.append(Snake(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), is_bot=True))

    # --- ОТРИСОВКА ---
    screen.fill(BG_COLOR)
    
    if player.alive:
        cam_x = player.x - WIDTH // 2
        cam_y = player.y - HEIGHT // 2
    cam_x = max(0, min(WORLD_SIZE - WIDTH, cam_x))
    cam_y = max(0, min(WORLD_SIZE - HEIGHT, cam_y))
    
    # Сетка (параллакс эффект, чуть темнее)
    off_x = int(cam_x) % 100
    off_y = int(cam_y) % 100
    for x in range(-off_x, WIDTH, 100):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(-off_y, HEIGHT, 100):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

    # Отрисовка объектов (по слоям)
    for bh in black_holes: bh.draw(screen, cam_x, cam_y)
    for f in foods: f.draw(screen, cam_x, cam_y)
    for p in particles: p.draw(screen, cam_x, cam_y)
    for b in bots: b.draw(screen, cam_x, cam_y)
    if player.alive: player.draw(screen, cam_x, cam_y)

    # Интерфейс
    # Score
    score_surf = font_big.render(str(int(player.length_float)), True, (255, 255, 255))
    score_surf.set_alpha(100) # полупрозрачный счет на фоне
    screen.blit(score_surf, (WIDTH - 150, HEIGHT - 100))
    
    # Инструкция
    info_txt = font_ui.render("SPACE to Boost | 'E' for GHOST MODE", True, (150, 255, 150))
    screen.blit(info_txt, (20, HEIGHT - 40))

    # Мини-карта
    mw, mh = 200, 200
    mx, my = WIDTH - mw - 20, 20
    pygame.draw.rect(screen, (0, 0, 0, 200), (mx, my, mw, mh))
    pygame.draw.rect(screen, (50, 50, 100), (mx, my, mw, mh), 2)
    
    # Игрок на карте
    if player.alive:
        px = mx + (player.x / WORLD_SIZE) * mw
        py = my + (player.y / WORLD_SIZE) * mh
        pygame.draw.circle(screen, (0, 255, 0), (int(px), int(py)), 3)
        
    # Черные дыры на карте
    for bh in black_holes:
        bx = mx + (bh.x / WORLD_SIZE) * mw
        by = my + (bh.y / WORLD_SIZE) * mh
        pygame.draw.circle(screen, (200, 0, 200), (int(bx), int(by)), 4)

    if game_over:
        t1 = font_big.render("WASTED", True, (255, 0, 50))
        t2 = font_ui.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 50))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
