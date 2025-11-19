# PGame
My project about pygame
import pygame
import random
import math
import sys

# --- настройки ---
WIDTH, HEIGHT = 800, 600          # размер окна
WORLD_W, WORLD_H = 3000, 3000     # размер «карты» (как у Slither.io)
BG_COLOR = (20, 20, 30)
FOOD_COLOR = (255, 200, 50)
SNAKE_COLOR = (100, 255, 100)
SNAKE_BASE_RADIUS = 8
SNAKE_SEG_DIST = 10               # расстояние между сегментами
SNAKE_SPEED = 3.0                 # базовая скорость
FOOD_COUNT = 400

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slither.io на pygame (singleplayer)")
clock = pygame.time.Clock()

# --- утилиты ---


def vec_len(v):
    return math.hypot(v[0], v[1])


def norm_vec(v):
    l = vec_len(v)
    if l == 0:
        return (0, 0)
    return (v[0] / l, v[1] / l)


def clamp(x, a, b):
    return max(a, min(b, x))


# --- еда ---


def spawn_food(n):
    food = []
    for _ in range(n):
        x = random.randint(0, WORLD_W)
        y = random.randint(0, WORLD_H)
        r = random.randint(2, 4)
        color = (
            random.randint(180, 255),
            random.randint(100, 255),
            random.randint(50, 255),
        )
        food.append({"pos": [x, y], "r": r, "color": color})
    return food


food_list = spawn_food(FOOD_COUNT)

# --- змейка ---


class Snake:
    def __init__(self, x, y):
        self.head = [x, y]
        self.segments = []
        self.length = 40  # стартовая длина (кол-во точек)
        # инициализация тела (хвост лежит за головой)
        for i in range(self.length):
            self.segments.append([x - i * SNAKE_SEG_DIST, y])
        self.score = 0

    def update(self, dt, target_pos):
        # направление к цели
        dir_vec = (target_pos[0] - self.head[0],
                   target_pos[1] - self.head[1])
        dir_vec = norm_vec(dir_vec)

        # уменьшение скорости при росте (примерно как в Slither.io)
        speed = SNAKE_SPEED * (0.6 + 0.4 * (40 / max(40, len(self.segments))))
        move = (dir_vec[0] * speed * dt, dir_vec[1] * speed * dt)

        # двигаем голову
        self.head[0] += move[0]
        self.head[1] += move[1]

        # не выходим за границы мира
        self.head[0] = clamp(self.head[0], 0, WORLD_W)
        self.head[1] = clamp(self.head[1], 0, WORLD_H)

        # первый сегмент = голова
        self.segments[0][0] = self.head[0]
        self.segments[0][1] = self.head[1]

        # каждый сегмент тянется за предыдущим
        for i in range(1, len(self.segments)):
            prev = self.segments[i - 1]
            cur = self.segments[i]
            vx = prev[0] - cur[0]
            vy = prev[1] - cur[1]
            dist = math.hypot(vx, vy)
            if dist == 0:
                continue
            # подвинуть на разницу до нужной дистанции
            diff = dist - SNAKE_SEG_DIST
            if abs(diff) > 0.1:
                nx = vx / dist
                ny = vy / dist
                cur[0] += nx * diff
                cur[1] += ny * diff

        # при большой длине можно немного «подрезать» хвост (оптимизация)
        # но для простоты это опустим

    def grow(self, amount):
        # добавляем сегменты к хвосту
        for _ in range(amount):
            tail = self.segments[-1]
            self.segments.append([tail[0], tail[1]])

    def draw(self, surf, cam_x, cam_y):
        # радиус зависит от длины (немного растёт)
        r = SNAKE_BASE_RADIUS + min(10, len(self.segments) // 30)
        # рисуем от хвоста к голове
        for i, seg in enumerate(self.segments):
            x = int(seg[0] - cam_x)
            y = int(seg[1] - cam_y)
            if -50 <= x <= WIDTH + 50 and -50 <= y <= HEIGHT + 50:
                pygame.draw.circle(surf, SNAKE_COLOR, (x, y), r)


player = Snake(WORLD_W // 2, WORLD_H // 2)

# --- главный цикл ---
running = True
while running:
    dt = clock.tick(60) / 16.0  # нормализация под 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # позиция мыши -> цель движения в координатах мира
    mx, my = pygame.mouse.get_pos()
    # камера центрируется на голове
    cam_x = player.head[0] - WIDTH // 2
    cam_y = player.head[1] - HEIGHT // 2
    target_world = (mx + cam_x, my + cam_y)

    # обновление змейки
    player.update(dt, target_world)

    # проверка поедания еды
    eaten = []
    for f in food_list:
        dx = f["pos"][0] - player.head[0]
        dy = f["pos"][1] - player.head[1]
        if dx * dx + dy * dy <= (SNAKE_BASE_RADIUS + 10) ** 2:
            eaten.append(f)
    for f in eaten:
        food_list.remove(f)
        player.grow(3)      # за каждую еду +3 сегмента
        player.score += 1
    # спавним еду заново, если стало мало
    if len(food_list) < FOOD_COUNT:
        food_list.extend(spawn_food(FOOD_COUNT - len(food_list)))

    # пересчёт камеры (после движения)
    cam_x = clamp(player.head[0] - WIDTH // 2, 0, max(0, WORLD_W - WIDTH))
    cam_y = clamp(player.head[1] - HEIGHT // 2, 0, max(0, WORLD_H - HEIGHT))

    # отрисовка
    screen.fill(BG_COLOR)

    # простая «сеточка» на фоне
    grid_step = 100
    grid_color = (40, 40, 60)
    for gx in range(0, WORLD_W + 1, grid_step):
        x = gx - cam_x
        if 0 <= x <= WIDTH:
            pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
    for gy in range(0, WORLD_H + 1, grid_step):
        y = gy - cam_y
        if 0 <= y <= HEIGHT:
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))

    # еда
    for f in food_list:
        x = int(f["pos"][0] - cam_x)
        y = int(f["pos"][1] - cam_y)
        if -10 <= x <= WIDTH + 10 and -10 <= y <= HEIGHT + 10:
            pygame.draw.circle(screen, f["color"], (x, y), f["r"])

    # змейка
    player.draw(screen, cam_x, cam_y)

    # простой HUD со счётом и длиной
    font = pygame.font.SysFont("consolas", 20)
    text = font.render(
        f"Score: {player.score}  Length: {len(player.segments)}", True, (255, 255, 255)
    )
    screen.blit(text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
