import json
import math
import os
import random

import pygame as pg


# настройки игры
FPS = 60
WIDTH = 1024
HEIGHT = 1024
TITLE = "Петля невозврата"
PLAYER_SPEED = 6
MAX_LOOPS = 6

# состояния игры
STATE_MENU = "MENU"
STATE_CROSSROAD = "CROSSROAD"
STATE_ROOM = "ROOM"
STATE_DIALOGUE = "DIALOGUE"
STATE_PAUSE = "PAUSE"
STATE_ENDING = "ENDING"

# комнаты
ROOM_THEATER = "THEATER"
ROOM_FUTURE = "FUTURE"
ROOM_LIBRARY = "LIBRARY"

# музыка. Если отдельного трека нет, игра попробует music/song.mp3
MUSIC_DEFAULT = "music/song.mp3"
MUSIC = {
    "menu": "music/menu.mp3",
    "crossroad": "music/crossroad.mp3",
    "theater": "music/theater.mp3",
    "future": "music/future.mp3",
    "library": "music/library.mp3",
    "ending": "music/ending.mp3",
}

# все координаты, которые чаще всего приходится подгонять вручную
ROOM_LAYOUT = {
    "crossroad": {
        "left_zone": [35, 390, 250, 260],
        "right_zone": [740, 390, 250, 260],
        "forward_zone": [405, 35, 220, 180],
        "bg_pos": [0, 0],
        "paths_pos": [0, 0],
        "steps_pos": [0, 0],
        "fountain_pos": [384, 340],
    },
    ROOM_THEATER: {
        "interact": [420, 510, 190, 130],
        "door_rect": [150, 100, 750, 300],
        "player_spawn": [512, 500],
        "stage_pos": [0, 0],
        "back_curtain_pos": [86, 0],
        "door_light_pos": [35, 100],
        "door_open_pos": [156, 100],
        "dummy1_pos": [250, 250],
        "dummy2_pos": [560, 420],
        "spotlight1_pos": [410, 0],
        "spotlight2_pos": [30, 0],
        "front_curtain_pos": [79, 0],
    },
    ROOM_FUTURE: {
        "interact": [420, 560, 190, 120],
        "door_rect": [440, 145, 145, 120],
        "player_spawn": [512, 900],
        "room_pos": [0, 0],
        "wall_pos": [50, 0],
        "door_locked_pos": [405, 72],
        "door_open_pos": [405, 72],
    },
    ROOM_LIBRARY: {
        "interact": [430, 560, 170, 130],
        "door_rect": [435, 130, 155, 130],
        "player_spawn": [512, 900],
        "bg_pos": [0, 0],
        "door_light_pos": [150, 0],
        "door_open_pos": [363, 0],
        "passage_pos": [363, 0],
        "cabinet_left_pos": [75, 0],
        "cabinet_right_pos": [525, 0],
        "paper1_pos": [220, 780],
        "paper2_pos": [430, 830],
        "paper3_pos": [720, 800],
        "table_pos": [335, 610],
        "flower_pos": [580, 525],
        "lamp_pos": [482, 0],
        "lamp_light_pos": [387, 45],
        "lamp_glow_pos": [402, 10],
        "cabinet_open_distance": 170,
        "smoke_top_pos": [0, 0],
    },
}


def clamp(value, low, high):
    return max(low, min(high, value))


def load_image(path, size=None):
    try:
        image = pg.image.load(path).convert_alpha()
    except Exception:
        # если ассета нет, игра не падает, а показывает яркую заглушку
        if size:
            image = pg.Surface(size, pg.SRCALPHA)
        else:
            image = pg.Surface((100, 100), pg.SRCALPHA)
        image.fill((220, 30, 220, 180))
        return image

    if size:
        image = pg.transform.scale(image, size)
    return image


def draw_text_center(screen, text, font, color, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    line = ""

    for word in words:
        candidate = (line + " " + word).strip()
        if font.size(candidate)[0] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)
    return lines


def draw_rotated(screen, image, x, y, angle):
    rect = image.get_rect(topleft=(x, y))
    rotated_image = pg.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=rect.center)
    screen.blit(rotated_image, rotated_rect)


def smooth_step(value):
    value = clamp(value, 0, 1)
    return value * value * (3 - 2 * value)


class Player:
    def __init__(self):
        self.image = load_image(r"images/character/Человек в мантии.png", (76, 128))
        self.rect = self.image.get_rect()
        self.speed = PLAYER_SPEED
        self.rect.center = (WIDTH // 2, 930)

    def set_center(self, pos):
        self.rect.center = pos

    def move(self):
        keys = pg.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            dx -= self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            dx += self.speed
        if keys[pg.K_UP] or keys[pg.K_w]:
            dy -= self.speed
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            dy += self.speed

        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = int(clamp(self.rect.x, 0, WIDTH - self.rect.width))
        self.rect.y = int(clamp(self.rect.y, 0, HEIGHT - self.rect.height))

    def draw(self, screen):
        shadow = pg.Rect(self.rect.x + 8, self.rect.bottom - 12, self.rect.width - 16, 12)
        pg.draw.ellipse(screen, (20, 20, 20), shadow)
        screen.blit(self.image, self.rect)


class Cloud:
    def __init__(self, image):
        self.image = image
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(60, 370)
        self.speed = random.uniform(0.8, 2.2)
        self.wait = random.randint(0, 260)

    def move(self):
        if self.wait > 0:
            self.wait -= 1
            return

        self.x -= self.speed
        if self.x < -self.image.get_width():
            self.wait = random.randint(240, 620)
            self.x = WIDTH + random.randint(20, 350)
            self.y = random.randint(60, 370)
            self.speed = random.uniform(0.8, 2.4)

    def draw(self, screen):
        if self.wait <= 0:
            screen.blit(self.image, (int(self.x), int(self.y)))


class MusicManager:
    def __init__(self):
        self.current_track = None

    def play(self, track_name):
        if self.current_track == track_name:
            return

        self.current_track = track_name
        path = MUSIC.get(track_name, MUSIC_DEFAULT)
        if not os.path.exists(path):
            path = MUSIC_DEFAULT
        if not os.path.exists(path):
            return

        try:
            pg.mixer.music.load(path)
            pg.mixer.music.set_volume(0.45)
            pg.mixer.music.play(-1)
        except Exception:
            pass


class ScenarioManager:
    def __init__(self):
        self.events = self.load_events()

    def load_events(self):
        try:
            with open("events.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
        return []

    def choose_for_room(self, room_id):
        variants = []
        for event in self.events:
            if str(event.get("room", "")).upper() == room_id:
                variants.append(event)

        if variants:
            return random.choice(variants)
        if self.events:
            return random.choice(self.events)

        return {
            "title": "Пустая комната",
            "description": "Событие не найдено. Проверь файл events.json.",
            "choices": [
                {"text": "Продолжить", "effects": {"humanity": 0, "logic": 0, "entropy": 0}},
                {"text": "Продолжить иначе", "effects": {"humanity": 0, "logic": 0, "entropy": 0}},
            ],
        }


class Crossroad:
    def __init__(self):
        self.layout = ROOM_LAYOUT["crossroad"]
        self.bg = load_image(r"images/crossroad/Каменный фон.png", (WIDTH, HEIGHT))
        self.paths = load_image(r"images/crossroad/Перекрёсток.png", (WIDTH, HEIGHT))
        self.steps = load_image(r"images/crossroad/Стопы.png", (WIDTH, HEIGHT))
        self.fountain = load_image(r"images/crossroad/Group 79.png")

        cloud_images = [
            load_image(r"images/crossroad/Облако1.png"),
            load_image(r"images/crossroad/Облако2.png"),
            load_image(r"images/crossroad/Облако3.png"),
            load_image(r"images/crossroad/Облако4.png"),
            load_image(r"images/crossroad/Облако5.png"),
        ]

        self.clouds = []
        for i in range(4):
            self.clouds.append(Cloud(cloud_images[i % len(cloud_images)]))

        self.zones = {
            "left": self.make_rect(self.layout["left_zone"]),
            "right": self.make_rect(self.layout["right_zone"]),
            "forward": self.make_rect(self.layout["forward_zone"]),
        }

    def make_rect(self, values):
        return pg.Rect(values[0], values[1], values[2], values[3])

    def update(self):
        for cloud in self.clouds:
            cloud.move()

    def check_transition(self, player_rect):
        if player_rect.colliderect(self.zones["left"]):
            return True
        if player_rect.colliderect(self.zones["right"]):
            return True
        if player_rect.colliderect(self.zones["forward"]):
            return True
        return False

    def draw(self, screen, player, font_small, loop_count):
        screen.blit(self.bg, self.layout["bg_pos"])
        screen.blit(self.paths, self.layout["paths_pos"])
        screen.blit(self.steps, self.layout["steps_pos"])
        screen.blit(self.fountain, self.layout["fountain_pos"])

        left_text = font_small.render("Налево", True, (240, 240, 240))
        right_text = font_small.render("Направо", True, (240, 240, 240))
        forward_text = font_small.render("Прямо", True, (240, 240, 240))
        screen.blit(left_text, (60, 400))
        screen.blit(right_text, (860, 400))
        screen.blit(forward_text, (470, 35))

        player.draw(screen)

        # облака идут поверх игрока и фонтана
        for cloud in self.clouds:
            cloud.draw(screen)

        draw_hud(screen, font_small, loop_count)
        draw_text_center(screen, "Иди по следам в туман", font_small, (240, 240, 240), 985)


class BaseRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.layout = ROOM_LAYOUT[room_id]
        self.door_open = False
        self.anim = 0

        self.interact_rect = self.make_rect(self.layout["interact"])
        self.door_rect = self.make_rect(self.layout["door_rect"])
        self.player_spawn = (self.layout["player_spawn"][0], self.layout["player_spawn"][1])

    def make_rect(self, values):
        return pg.Rect(values[0], values[1], values[2], values[3])

    def reset(self):
        self.door_open = False
        self.anim = 0

    def open_door(self):
        self.door_open = True
        self.anim = 0

    def update(self):
        if self.door_open and self.anim < 70:
            self.anim += 1

    def can_interact(self, player_rect):
        return player_rect.colliderect(self.interact_rect) and not self.door_open

    def can_exit(self, player_rect):
        return player_rect.colliderect(self.door_rect) and self.door_open

    def draw_prompt(self, screen, player_rect, font_small):
        if self.can_interact(player_rect):
            prompt = font_small.render("Нажми E", True, (255, 255, 255))
            screen.blit(prompt, (self.interact_rect.x + 48, self.interact_rect.y - 28))

        if player_rect.colliderect(self.door_rect) and not self.door_open:
            text = font_small.render("Сначала сделай выбор", True, (255, 220, 220))
            screen.blit(text, (self.door_rect.x - 25, self.door_rect.bottom + 10))


class TheaterRoom(BaseRoom):
    def __init__(self):
        BaseRoom.__init__(self, ROOM_THEATER)
        self.stage = load_image(r"images/room1/Сцена.png")
        self.back_curtain = load_image(r"images/room1/Задний занавес.png")
        self.front_curtain = load_image(r"images/room1/Занавес.png")
        self.dummy1 = load_image(r"images/room1/Манекен1.png")
        self.dummy2 = load_image(r"images/room1/Манекен2.png")
        self.spotlight1 = load_image(r"images/room1/Свет1.png")
        self.spotlight2 = load_image(r"images/room1/Свет2.png")
        self.door_open_image = load_image(r"images/room1/Дверь светлая.png")
        self.door_light = load_image(r"images/room1/свет от двери.png")

    def draw(self, screen, player, font_small, tick):
        screen.fill((15, 15, 18))
        screen.blit(self.stage, self.layout["stage_pos"])
        screen.blit(self.back_curtain, self.layout["back_curtain_pos"])

        if self.door_open:
            screen.blit(self.door_light, self.layout["door_light_pos"])
            screen.blit(self.door_open_image, self.layout["door_open_pos"])

        screen.blit(self.dummy1, self.layout["dummy1_pos"])
        screen.blit(self.dummy2, self.layout["dummy2_pos"])

        alpha = 165 + int(80 * abs(math.sin(tick * 0.04)))
        light1 = self.spotlight1.copy()
        light2 = self.spotlight2.copy()
        light1.set_alpha(alpha)
        light2.set_alpha(alpha)
        screen.blit(light1, self.layout["spotlight1_pos"])
        screen.blit(light2, self.layout["spotlight2_pos"])

        screen.blit(self.front_curtain, self.layout["front_curtain_pos"])
        self.draw_prompt(screen, player.rect, font_small)
        draw_text_center(screen, "Театр", font_small, (244, 244, 244), 68)
        player.draw(screen)


class FutureRoom(BaseRoom):
    def __init__(self):
        BaseRoom.__init__(self, ROOM_FUTURE)
        self.room = load_image(r"images/room2/Пол.png")
        self.wall = load_image(r"images/room2/Стена.png")
        self.locked_door = load_image(r"images/room2/Дверь Locked.png")
        self.open_door_image = load_image(r"images/room2/Дверь открытая.png")

    def draw(self, screen, player, font_small, tick):
        screen.blit(self.room, self.layout["room_pos"])
        screen.blit(self.wall, self.layout["wall_pos"])

        if self.door_open:
            screen.blit(self.open_door_image, self.layout["door_open_pos"])
        else:
            screen.blit(self.locked_door, self.layout["door_locked_pos"])

        self.draw_prompt(screen, player.rect, font_small)
        draw_text_center(screen, "Футуристичный сектор", font_small, (244, 244, 244), 68)
        player.draw(screen)


class LibraryRoom(BaseRoom):
    def __init__(self):
        BaseRoom.__init__(self, ROOM_LIBRARY)
        self.bg = load_image(r"images/room3/Фон.png")
        self.black_passage = load_image(r"images/room3/Чёрный проход.png")
        self.left_cabinet = load_image(r"images/room3/Шкаф.png")
        self.right_cabinet = load_image(r"images/room3/Шкаф-1.png")
        self.lamp = load_image(r"images/room3/Лампа.png")
        self.lamp_glow = load_image(r"images/room3/Свечение лампы.png")
        self.lamp_light = load_image(r"images/room3/Свет от лампы.png")
        self.table = load_image(r"images/room3/Стол.png")
        self.flower = load_image(r"images/room3/Цветок.png")
        self.paper1 = load_image(r"images/room3/Листок.png")
        self.paper2 = load_image(r"images/room3/Листок1.png")
        self.paper3 = load_image(r"images/room3/Листок2.png")
        self.smoke = load_image(r"images/room3/Черный туман сверху(дымка).png")
        self.open_door_image = load_image(r"images/room3/Светлая дверь.png")
        self.door_light = load_image(r"images/room3/свет от двери.png")

    def draw(self, screen, player, font_small, tick):
        screen.blit(self.bg, self.layout["bg_pos"])

        open_progress = smooth_step(self.anim / 70)
        cabinet_offset = int(self.layout["cabinet_open_distance"] * open_progress)

        if self.door_open:
            screen.blit(self.door_light, self.layout["door_light_pos"])
            screen.blit(self.open_door_image, self.layout["door_open_pos"])
        else:
            screen.blit(self.black_passage, self.layout["passage_pos"])

        left_pos = self.layout["cabinet_left_pos"]
        right_pos = self.layout["cabinet_right_pos"]
        screen.blit(self.left_cabinet, (left_pos[0] - cabinet_offset, left_pos[1]))
        screen.blit(self.right_cabinet, (right_pos[0] + cabinet_offset, right_pos[1]))

        screen.blit(self.paper1, self.layout["paper1_pos"])
        screen.blit(self.paper2, self.layout["paper2_pos"])
        screen.blit(self.paper3, self.layout["paper3_pos"])
        screen.blit(self.table, self.layout["table_pos"])
        screen.blit(self.flower, self.layout["flower_pos"])

        lamp_angle = math.sin(tick * 0.028 + math.sin(tick * 0.011) * 1.4) * 7
        lamp_angle += math.sin(tick * 0.006) * 2

        glow = self.lamp_glow.copy()
        glow.set_alpha(120 + int(120 * abs(math.sin(tick * 0.04))))
        draw_rotated(screen, self.lamp_light, self.layout["lamp_light_pos"][0], self.layout["lamp_light_pos"][1], lamp_angle)
        draw_rotated(screen, glow, self.layout["lamp_glow_pos"][0], self.layout["lamp_glow_pos"][1], lamp_angle)
        draw_rotated(screen, self.lamp, self.layout["lamp_pos"][0], self.layout["lamp_pos"][1], lamp_angle)

        screen.blit(self.smoke, self.layout["smoke_top_pos"])
        self.draw_prompt(screen, player.rect, font_small)
        draw_text_center(screen, "Библиотека", font_small, (244, 244, 244), 68)
        player.draw(screen)


class ChoiceMenu:
    def __init__(self):
        self.button_image = load_image(r"images/Button.png")
        self.font_button = pg.font.Font(None, 31)

    def draw(self, screen, event, selected, font_title, font_text):
        panel = pg.Rect(120, 160, 784, 560)
        pg.draw.rect(screen, (18, 18, 25), panel, 0, 12)
        pg.draw.rect(screen, (170, 170, 185), panel, 2, 12)

        title = event.get("title", "Событие")
        title_surf = font_title.render(title, True, (245, 245, 245))
        screen.blit(title_surf, (panel.x + 25, panel.y + 20))

        lines = wrap_text(event.get("description", ""), font_text, panel.width - 50)
        y = panel.y + 78
        for line in lines:
            surf = font_text.render(line, True, (220, 220, 226))
            screen.blit(surf, (panel.x + 25, y))
            y += 34

        choices = event.get("choices", [])
        for i, choice in enumerate(choices):
            self.draw_button(screen, panel, choice, i, selected)

        hint = font_text.render("1/2 или стрелки + Enter", True, (190, 190, 206))
        screen.blit(hint, (panel.x + 25, panel.bottom - 36))

    def draw_button(self, screen, panel, choice, index, selected):
        button_width = 340
        button_height = 96

        if index == 0:
            rect = pg.Rect(panel.x + 35, panel.y + 355, button_width, button_height)
        else:
            rect = pg.Rect(panel.right - 35 - button_width, panel.y + 355, button_width, button_height)

        button = pg.transform.scale(self.button_image, (rect.width, rect.height))
        if index == selected:
            glow_rect = pg.Rect(rect.x - 6, rect.y - 6, rect.width + 12, rect.height + 12)
            pg.draw.rect(screen, (215, 215, 180), glow_rect, 3, 10)
        screen.blit(button, rect)

        text = str(index + 1) + ". " + choice.get("text", "...")
        lines = wrap_text(text, self.font_button, rect.width - 42)
        line_height = 28
        text_y = rect.centery - (len(lines) * line_height) // 2

        for line in lines:
            surf = self.font_button.render(line, True, (245, 245, 245))
            screen.blit(surf, (rect.centerx - surf.get_width() // 2, text_y))
            text_y += line_height


def draw_hud(screen, font, loop_count):
    text = "Круг: " + str(loop_count) + "/" + str(MAX_LOOPS)
    panel = pg.Rect(12, 10, 140, 40)
    pg.draw.rect(screen, (10, 10, 10), panel, 0, 8)
    pg.draw.rect(screen, (150, 150, 165), panel, 2, 8)
    surf = font.render(text, True, (245, 245, 245))
    screen.blit(surf, (20, 19))


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

        self.font_small = pg.font.Font(None, 32)
        self.font_text = pg.font.Font(None, 38)
        self.font_title = pg.font.Font(None, 52)
        self.font_big = pg.font.Font(None, 82)

        self.player = Player()
        self.crossroad = Crossroad()
        self.scenarios = ScenarioManager()
        self.music = MusicManager()
        self.choice_menu = ChoiceMenu()

        self.rooms = {
            ROOM_THEATER: TheaterRoom(),
            ROOM_FUTURE: FutureRoom(),
            ROOM_LIBRARY: LibraryRoom(),
        }

        self.running = True
        self.state = STATE_MENU
        self.prev_state = STATE_CROSSROAD
        self.current_room = None
        self.current_event = None
        self.selected_choice = 0
        self.last_room_id = None
        self.loop_count = 0
        self.tick = 0
        self.ending_text = ""
        self.stats = {"humanity": 0, "logic": 0, "entropy": 0}

    def reset_run(self):
        self.state = STATE_CROSSROAD
        self.prev_state = STATE_CROSSROAD
        self.current_room = None
        self.current_event = None
        self.selected_choice = 0
        self.last_room_id = None
        self.loop_count = 0
        self.ending_text = ""
        self.stats = {"humanity": 0, "logic": 0, "entropy": 0}
        self.player.set_center((WIDTH // 2, 930))

        for room in self.rooms.values():
            room.reset()

    def choose_room_id(self):
        room_ids = [ROOM_THEATER, ROOM_FUTURE, ROOM_LIBRARY]
        variants = []
        for room_id in room_ids:
            if room_id != self.last_room_id:
                variants.append(room_id)

        if not variants:
            variants = room_ids
        return random.choice(variants)

    def start_random_room(self):
        room_id = self.choose_room_id()
        self.current_room = self.rooms[room_id]
        self.current_room.reset()
        self.current_event = self.scenarios.choose_for_room(room_id)
        self.last_room_id = room_id
        self.selected_choice = 0
        self.player.set_center(self.current_room.player_spawn)
        self.state = STATE_ROOM

    def apply_choice(self, choice_index):
        choices = self.current_event.get("choices", [])
        if choice_index < 0 or choice_index >= len(choices):
            return

        effects = choices[choice_index].get("effects", {})
        self.stats["humanity"] += int(effects.get("humanity", 0))
        self.stats["logic"] += int(effects.get("logic", 0))
        self.stats["entropy"] += int(effects.get("entropy", 0))
        self.current_room.open_door()
        self.state = STATE_ROOM

    def get_ending_text(self):
        humanity = self.stats["humanity"]
        logic = self.stats["logic"]
        entropy = self.stats["entropy"]

        if entropy >= max(humanity, logic) + 2:
            return "Сбой системы: хаос разрушил петлю, и мир рассыпался на части."
        if logic >= humanity + 3 and logic >= entropy + 2:
            return "Абсолютный прагматик: ты спас систему, но потерял все личное."
        if humanity >= logic + 3 and humanity >= entropy + 2:
            return "Последний человек: ты спасал других, но остался в петле один."
        return "Идеальный баланс: ты не выбрал сторону, и петля замкнулась снова."

    def update_music(self):
        if self.state == STATE_MENU:
            self.music.play("menu")
        elif self.state == STATE_CROSSROAD:
            self.music.play("crossroad")
        elif self.state == STATE_ENDING:
            self.music.play("ending")
        elif self.current_room:
            if self.current_room.room_id == ROOM_THEATER:
                self.music.play("theater")
            elif self.current_room.room_id == ROOM_FUTURE:
                self.music.play("future")
            elif self.current_room.room_id == ROOM_LIBRARY:
                self.music.play("library")

    def handle_keydown(self, key):
        if key == pg.K_ESCAPE:
            if self.state == STATE_PAUSE:
                self.state = self.prev_state
            elif self.state in [STATE_CROSSROAD, STATE_ROOM, STATE_DIALOGUE]:
                self.prev_state = self.state
                self.state = STATE_PAUSE

        if self.state == STATE_MENU:
            if key == pg.K_RETURN:
                self.reset_run()

        elif self.state == STATE_ROOM:
            if key == pg.K_e and self.current_room.can_interact(self.player.rect):
                self.selected_choice = 0
                self.state = STATE_DIALOGUE

        elif self.state == STATE_DIALOGUE:
            self.handle_dialogue_key(key)

        elif self.state == STATE_ENDING:
            if key == pg.K_r:
                self.reset_run()
            elif key == pg.K_q:
                self.running = False

        elif self.state == STATE_PAUSE:
            if key == pg.K_r:
                self.reset_run()

    def handle_dialogue_key(self, key):
        choices = self.current_event.get("choices", [])

        if key in [pg.K_1, pg.K_KP1] and len(choices) > 0:
            self.apply_choice(0)
        elif key in [pg.K_2, pg.K_KP2] and len(choices) > 1:
            self.apply_choice(1)
        elif key == pg.K_UP:
            self.selected_choice = max(0, self.selected_choice - 1)
        elif key == pg.K_DOWN:
            self.selected_choice = min(len(choices) - 1, self.selected_choice + 1)
        elif key == pg.K_LEFT:
            self.selected_choice = 0
        elif key == pg.K_RIGHT and len(choices) > 1:
            self.selected_choice = 1
        elif key == pg.K_RETURN and choices:
            self.apply_choice(self.selected_choice)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self.handle_keydown(event.key)

    def update(self):
        if self.state in [STATE_CROSSROAD, STATE_ROOM]:
            self.player.move()

        if self.state == STATE_CROSSROAD:
            self.crossroad.update()
            if self.crossroad.check_transition(self.player.rect):
                self.start_random_room()

        elif self.state == STATE_ROOM:
            self.current_room.update()
            if self.current_room.can_exit(self.player.rect):
                self.loop_count += 1
                if self.loop_count >= MAX_LOOPS:
                    self.ending_text = self.get_ending_text()
                    self.state = STATE_ENDING
                else:
                    self.player.set_center((WIDTH // 2, 930))
                    self.state = STATE_CROSSROAD

        self.update_music()

    def draw_menu(self):
        self.screen.fill((12, 13, 20))
        draw_text_center(self.screen, TITLE, self.font_big, (245, 245, 250), 250)
        draw_text_center(self.screen, "Enter - начать", self.font_title, (220, 220, 230), 410)
        draw_text_center(self.screen, "WASD/Стрелки - движение", self.font_small, (200, 200, 212), 500)
        draw_text_center(self.screen, "E - выбор в комнате", self.font_small, (200, 200, 212), 540)
        draw_text_center(self.screen, "Esc - пауза", self.font_small, (200, 200, 212), 580)

    def draw_current_room(self):
        self.current_room.draw(self.screen, self.player, self.font_small, self.tick)
        draw_hud(self.screen, self.font_small, self.loop_count)

    def draw_dialogue(self):
        self.draw_current_room()
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        self.choice_menu.draw(self.screen, self.current_event, self.selected_choice, self.font_title, self.font_text)
        draw_hud(self.screen, self.font_small, self.loop_count)

    def draw_pause(self):
        if self.prev_state in [STATE_ROOM, STATE_DIALOGUE]:
            self.draw_current_room()
        else:
            self.crossroad.draw(self.screen, self.player, self.font_small, self.loop_count)

        dark = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        dark.fill((0, 0, 0, 160))
        self.screen.blit(dark, (0, 0))
        draw_text_center(self.screen, "Пауза", self.font_big, (245, 245, 245), 350)
        draw_text_center(self.screen, "Esc - продолжить", self.font_title, (220, 220, 220), 470)
        draw_text_center(self.screen, "R - заново", self.font_title, (220, 220, 220), 530)

    def draw_ending(self):
        self.screen.fill((10, 10, 14))
        draw_text_center(self.screen, "Финал", self.font_big, (245, 245, 245), 180)

        lines = wrap_text(self.ending_text, self.font_title, 860)
        y = 360
        for line in lines:
            draw_text_center(self.screen, line, self.font_title, (220, 220, 228), y)
            y += 56

        stat_text = "Humanity: " + str(self.stats["humanity"])
        stat_text += " | Logic: " + str(self.stats["logic"])
        stat_text += " | Entropy: " + str(self.stats["entropy"])
        draw_text_center(self.screen, stat_text, self.font_small, (200, 200, 210), 690)
        draw_text_center(self.screen, "R - заново    Q - выход", self.font_title, (220, 220, 230), 810)

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_CROSSROAD:
            self.crossroad.draw(self.screen, self.player, self.font_small, self.loop_count)
        elif self.state == STATE_ROOM:
            self.draw_current_room()
        elif self.state == STATE_DIALOGUE:
            self.draw_dialogue()
        elif self.state == STATE_PAUSE:
            self.draw_pause()
        elif self.state == STATE_ENDING:
            self.draw_ending()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.tick += 1
            self.handle_events()
            self.update()
            self.draw()
            pg.display.update()

        pg.quit()


game = Game()
game.run()
