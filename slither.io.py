import pygame
import random
import math
import sys

# --- КОНФИГУРАЦИЯ ---
WIDTH, HEIGHT = 1280, 720        # Размер окна
WORLD_SIZE = 4000                # Размер игрового мира
BG_COLOR = (15, 15, 20)          # Темный фон
GRID_COLOR = (40, 40, 50)
FPS = 60

# Параметры змейки
BASE_RADIUS = 10
SEGMENT_DIST = 6                 # Дистанция между кружками тела
SPEED_NORMAL = 4.0
SPEED_BOOST = 7.0
TURN_SPEED = 0.25                # Скорость поворота (рад/кадр)
START_LENGTH = 20                # Стартовая длина
BOOST_COST = 0.5                 # Сколько длины теряем за кадр при бусте

# Еда
FOOD_COUNT = 800
FOOD_SIZE_MIN = 3
FOOD_SIZE_MAX = 7
FOOD_ENERGY_SMALL = 1
FOOD_ENERGY_CORPSE = 5           # Энергия от "трупа" змеи

# Цвета (яркие, неоновые)
COLORS = [
    (255, 50, 50), (50, 255, 50), (50, 50, 255),
    (255, 255, 50), (50, 255, 255), (255, 50, 255),
    (255, 150, 50), (150, 50, 255), (50, 255, 150)
]

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slither.io Clone - Pygame (AI + Boost + Combat)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)
font_big = pygame.font.SysFont("arial", 50, bold=True)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_random_color():
    return random.choice(COLORS)

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# --- КЛАССЫ ---

class Food:
    def __init__(self, x, y, radius, energy, color=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.energy = energy
        self.color = color if color else (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.glow_tick = random.randint(0, 60)

    def draw(self, surface, cam_x, cam_y):
        sx = self.x - cam_x
        sy = self.y - cam_y
        # Оптимизация: не рисуем, если за экраном
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            # Эффект пульсации
            pulsate = math.sin(pygame.time.get_ticks() * 0.01 + self.glow_tick) * 1.5
            curr_r = max(2, self.radius + pulsate)
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), int(curr_r))

class Snake:
    def __init__(self, x, y, is_bot=False, name="Bot"):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, math.pi * 2)
        self.target_angle = self.angle
        self.speed = SPEED_NORMAL
        self.radius = BASE_RADIUS
        self.color = get_random_color()
        # Храним координаты каждого сегмента
        self.segments = []
        for i in range(START_LENGTH):
            self.segments.append({'x': x - i * SEGMENT_DIST, 'y': y})
        
        self.length_float = float(START_LENGTH) # Дробная длина для плавного роста
        self.is_bot = is_bot
        self.name = name
        self.alive = True
        self.boosting = False
        
        # Для ИИ
        self.ai_change_dir_timer = 0
        self.ai_target_pos = None

    def update(self, dt, snakes_list, foods_list):
        if not self.alive: return

        # -- ЛОГИКА ПОВОРОТА --
        if not self.is_bot:
            # Управление игрока
            mx, my = pygame.mouse.get_pos()
            # Считаем угол к мыши относительно центра экрана (так как камера центрирована на змее)
            # Но "центр экрана" это (WIDTH/2, HEIGHT/2)
            dx = mx - WIDTH / 2
            dy = my - HEIGHT / 2
            self.target_angle = math.atan2(dy, dx)
            
            # Ускорение (пробел или клик)
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed()
            if (keys[pygame.K_SPACE] or mouse[0]) and self.length_float > 10:
                self.boosting = True
            else:
                self.boosting = False

        else:
            # Управление бота
            self.ai_logic(snakes_list, foods_list)

        # Плавный поворот к целевому углу
        diff = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        if abs(diff) < TURN_SPEED:
            self.angle = self.target_angle
        else:
            # Поворачиваем в нужную сторону
            if diff > 0:
                self.angle += TURN_SPEED
            else:
                self.angle -= TURN_SPEED
        self.angle %= 2 * math.pi

        # -- ДВИЖЕНИЕ ГОЛОВЫ --
        current_speed = SPEED_BOOST if self.boosting else SPEED_NORMAL
        
        # Трата массы при ускорении
        if self.boosting:
            self.length_float -= BOOST_COST
            # Спавним еду позади (след)
            if random.random() < 0.2: # Не каждый кадр
                tail = self.segments[-1]
                foods_list.append(Food(tail['x'], tail['y'], random.randint(2,4), 1, self.color))

        self.x += math.cos(self.angle) * current_speed
        self.y += math.sin(self.angle) * current_speed

        # Границы мира
        self.x = max(0, min(WORLD_SIZE, self.x))
        self.y = max(0, min(WORLD_SIZE, self.y))

        # -- ОБНОВЛЕНИЕ ТЕЛА --
        # Голова - новый сегмент
        self.segments.insert(0, {'x': self.x, 'y': self.y})
        
        # Удаляем лишние сегменты (хвост)
        target_len = int(self.length_float)
        while len(self.segments) > target_len:
            self.segments.pop()
        
        # "Подтягивание" сегментов для плавности (Inverse Kinematics like)
        # Проходимся по сегментам и держим их на дистанции SEGMENT_DIST
        for i in range(1, len(self.segments)):
            prev = self.segments[i-1]
            curr = self.segments[i]
            
            dx = curr['x'] - prev['x']
            dy = curr['y'] - prev['y']
            dist = math.hypot(dx, dy)
            
            # Если сегмент слишком близко/далеко, сдвигаем его
            # Но для "змейки" достаточно просто: curr встает на дистанцию от prev
            if dist > 0: # чтобы не делить на 0
                scale = SEGMENT_DIST / dist
                curr['x'] = prev['x'] + dx * scale
                curr['y'] = prev['y'] + dy * scale

        # -- РАДИУС --
        # Змея толстеет от длины
        self.radius = BASE_RADIUS + (self.length_float / 150.0)
        if self.radius > 25: self.radius = 25

    def ai_logic(self, snakes, foods):
        # Простейший ИИ: ищем ближайшую еду, избегаем других
        self.ai_change_dir_timer -= 1
        
        # 1. Избегание столкновений (Приоритет)
        danger_dist = self.radius * 4
        avoiding = False
        for s in snakes:
            if s == self or not s.alive: continue
            # Проверяем голову бота с телом другой змеи
            for seg in s.segments:
                d = distance((self.x, self.y), (seg['x'], seg['y']))
                if d < danger_dist:
                    # Опасность! Поворачиваем от точки
                    angle_to_danger = math.atan2(seg['y'] - self.y, seg['x'] - self.x)
                    self.target_angle = angle_to_danger + math.pi # Разворот на 180
                    self.boosting = True # Паническое ускорение
                    avoiding = True
                    break
            if avoiding: break
        
        if avoiding: return

        self.boosting = False # Если опасности нет, не тратим массу

        # 2. Поиск еды
        if self.ai_change_dir_timer <= 0:
            # Ищем еду в радиусе обзора
            view_dist = 400
            best_food = None
            min_dist = view_dist
            
            # Смотрим случайные 50 кусочков еды (оптимизация)
            sample_foods = random.sample(foods, min(50, len(foods))) if len(foods) > 50 else foods
            
            for f in sample_foods:
                d = distance((self.x, self.y), (f.x, f.y))
                if d < min_dist:
                    min_dist = d
                    best_food = f
            
            if best_food:
                self.target_angle = math.atan2(best_food.y - self.y, best_food.x - self.x)
            else:
                # Если еды нет, просто рандомно меняем угол немного
                self.target_angle += random.uniform(-1, 1)
                # Не уходить за границы
                if self.x < 100: self.target_angle = 0
                if self.x > WORLD_SIZE - 100: self.target_angle = math.pi
                if self.y < 100: self.target_angle = math.pi / 2
                if self.y > WORLD_SIZE - 100: self.target_angle = -math.pi / 2
            
            self.ai_change_dir_timer = random.randint(10, 60)

    def check_collision(self, other_snake):
        # Проверяет, врезалась ли ГОЛОВА self в ТЕЛО other_snake
        if not self.alive or not other_snake.alive: return False
        
        head_x, head_y = self.segments[0]['x'], self.segments[0]['y']
        
        # Начинаем проверку не с 0, чтобы не врезаться в свою голову, 
        # но тут other_snake - это другая змея
        
        # Оптимизация: сначала проверяем bounding box
        if abs(head_x - other_snake.x) > 200 or abs(head_y - other_snake.y) > 200: 
            if len(other_snake.segments) < 20: # Если короткая, может и не надо проверять далеко
                 return False

        start_index = 0
        if other_snake == self:
             # Самого себя можно укусить, если кольцо сделать, но обычно проверяют с индекса ~2
             start_index = 2 
        
        for i in range(start_index, len(other_snake.segments)):
            seg = other_snake.segments[i]
            # Проверка кругов
            dist_sq = (head_x - seg['x'])**2 + (head_y - seg['y'])**2
            radii_sum = self.radius * 0.8 + other_snake.radius # 0.8 чтобы хитбокс был чуть меньше (честнее)
            
            if dist_sq < radii_sum**2:
                return True
        return False

    def die(self, foods_list):
        self.alive = False
        # Превращение тела в еду
        step = 2 # Каждые 2 сегмента (чтобы не спамить едой)
        for i in range(0, len(self.segments), step):
            seg = self.segments[i]
            # Еда чуть больше обычной
            f = Food(seg['x'], seg['y'], random.randint(FOOD_SIZE_MIN, FOOD_SIZE_MAX+2), FOOD_ENERGY_CORPSE, self.color)
            foods_list.append(f)
            
    def draw(self, surface, cam_x, cam_y):
        if not self.alive: return
        
        # Рисуем от хвоста к голове, чтобы голова была сверху
        # Тело
        for seg in reversed(self.segments):
            sx = int(seg['x'] - cam_x)
            sy = int(seg['y'] - cam_y)
            if -50 <= sx <= WIDTH + 50 and -50 <= sy <= HEIGHT + 50:
                pygame.draw.circle(surface, self.color, (sx, sy), int(self.radius))
        
        # Голова (глаза)
        head = self.segments[0]
        hx = int(head['x'] - cam_x)
        hy = int(head['y'] - cam_y)
        
        if -50 <= hx <= WIDTH + 50 and -50 <= hy <= HEIGHT + 50:
             # Глаза
            eye_offset_x = math.cos(self.angle - 0.5) * (self.radius * 0.6)
            eye_offset_y = math.sin(self.angle - 0.5) * (self.radius * 0.6)
            
            eye2_offset_x = math.cos(self.angle + 0.5) * (self.radius * 0.6)
            eye2_offset_y = math.sin(self.angle + 0.5) * (self.radius * 0.6)
            
            # Белки
            pygame.draw.circle(surface, (255,255,255), (int(hx + eye_offset_x), int(hy + eye_offset_y)), int(self.radius*0.4))
            pygame.draw.circle(surface, (255,255,255), (int(hx + eye2_offset_x), int(hy + eye2_offset_y)), int(self.radius*0.4))
            
            # Зрачки (смотрят по направлению)
            pupil_dist = self.radius * 0.2
            px = math.cos(self.angle) * pupil_dist
            py = math.sin(self.angle) * pupil_dist
            
            pygame.draw.circle(surface, (0,0,0), (int(hx + eye_offset_x + px), int(hy + eye_offset_y + py)), int(self.radius*0.2))
            pygame.draw.circle(surface, (0,0,0), (int(hx + eye2_offset_x + px), int(hy + eye2_offset_y + py)), int(self.radius*0.2))
            
            # Имя
            if not self.is_bot:
                name_surf = font.render("You", True, (255, 255, 255))
                surface.blit(name_surf, (hx - name_surf.get_width()//2, hy - self.radius - 25))

# --- ГЛАВНЫЙ ЦИКЛ ---

# Создание объектов
foods = [Food(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), random.randint(FOOD_SIZE_MIN, FOOD_SIZE_MAX), FOOD_ENERGY_SMALL) for _ in range(FOOD_COUNT)]

player = Snake(WORLD_SIZE//2, WORLD_SIZE//2, is_bot=False)
bots = [Snake(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), is_bot=True, name=f"Bot{i}") for i in range(15)]

running = True
game_over = False

while running:
    dt = clock.tick(FPS) / 1000.0  # delta time в секундах (не используется глубоко, но полезно)
    
    # 1. События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Рестарт
                foods = [Food(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), random.randint(FOOD_SIZE_MIN, FOOD_SIZE_MAX), FOOD_ENERGY_SMALL) for _ in range(FOOD_COUNT)]
                player = Snake(WORLD_SIZE//2, WORLD_SIZE//2, is_bot=False)
                bots = [Snake(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), is_bot=True, name=f"Bot{i}") for i in range(15)]
                game_over = False
            if event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        all_snakes = [player] + bots
        
        # 2. Обновление и логика
        for s in all_snakes:
            s.update(dt, all_snakes, foods)

        # Проверка поедания еды
        # Оптимизация: проверяем только близкую еду (Spatial partitioning было бы лучше, но для 800 объектов brute force пойдет)
        for s in all_snakes:
            if not s.alive: continue
            # Простой итератор по копии, чтобы можно было удалять
            # Для оптимизации можно проверять расстояние квадратом
            head_x, head_y = s.segments[0]['x'], s.segments[0]['y']
            eat_radius_sq = (s.radius + 10) ** 2
            
            for f in foods[:]: # Копия списка
                dx = head_x - f.x
                dy = head_y - f.y
                if dx*dx + dy*dy < eat_radius_sq:
                    s.length_float += f.energy
                    foods.remove(f)
        
        # Пополнение еды
        if len(foods) < FOOD_COUNT:
            foods.append(Food(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), random.randint(FOOD_SIZE_MIN, FOOD_SIZE_MAX), FOOD_ENERGY_SMALL))

        # Столкновения змей (Бой)
        for i, s1 in enumerate(all_snakes):
            if not s1.alive: continue
            for s2 in all_snakes:
                if s1 == s2: continue
                if not s2.alive: continue
                
                if s1.check_collision(s2):
                    s1.die(foods) # s1 врезался в s2 -> s1 умирает
                    if s1 == player:
                        game_over = True

        # Респаун ботов
        for bot in bots:
            if not bot.alive:
                bots.remove(bot)
                new_bot = Snake(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), is_bot=True)
                bots.append(new_bot)

    # 3. Отрисовка
    screen.fill(BG_COLOR)
    
    # Камера следует за игроком (или за центром, если умер)
    if player.alive:
        cam_x = player.segments[0]['x'] - WIDTH // 2
        cam_y = player.segments[0]['y'] - HEIGHT // 2
    
    # Ограничение камеры краями мира
    cam_x = max(-WIDTH/2, min(WORLD_SIZE - WIDTH/2, cam_x))
    cam_y = max(-HEIGHT/2, min(WORLD_SIZE - HEIGHT/2, cam_y))
    
    # Сетка
    grid_offset_x = int(cam_x) % 50
    grid_offset_y = int(cam_y) % 50
    
    for x in range(-grid_offset_x, WIDTH, 50):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(-grid_offset_y, HEIGHT, 50):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

    # Еда
    for f in foods:
        f.draw(screen, cam_x, cam_y)
        
    # Змеи
    # Рисуем ботов
    for bot in bots:
        bot.draw(screen, cam_x, cam_y)
    # Игрок (поверх ботов)
    if player.alive:
        player.draw(screen, cam_x, cam_y)

    # UI
    score_text = font.render(f"Length: {int(player.length_float)}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))
    
    # Мини-карта
    map_size = 150
    map_x = WIDTH - map_size - 20
    map_y = HEIGHT - map_size - 20
    
    # Фон карты
    pygame.draw.rect(screen, (0, 0, 0, 150), (map_x, map_y, map_size, map_size))
    pygame.draw.rect(screen, (100, 100, 100), (map_x, map_y, map_size, map_size), 2)
    
    # Точки на карте
    def draw_on_map(obj_x, obj_y, color):
        mx = map_x + (obj_x / WORLD_SIZE) * map_size
        my = map_y + (obj_y / WORLD_SIZE) * map_size
        pygame.draw.circle(screen, color, (int(mx), int(my)), 2)

    if player.alive:
        draw_on_map(player.segments[0]['x'], player.segments[0]['y'], (0, 255, 0))
    
    for bot in bots:
        if bot.alive:
            draw_on_map(bot.segments[0]['x'], bot.segments[0]['y'], (255, 0, 0))

    if game_over:
        over_text = font_big.render("GAME OVER", True, (255, 50, 50))
        restart_text = font.render("Press 'R' to Restart", True, (200, 200, 200))
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
