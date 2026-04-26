import json
import math
import os
import random

import pygame as pg


FPS = 60
WIDTH = 1024
HEIGHT = 1024
TITLE = "Петля невозврата"
PLAYER_SPEED = 6
MAX_LOOPS = 6

STATE_MENU = "MENU"
STATE_CROSSROAD = "CROSSROAD"
STATE_ROOM = "ROOM"
STATE_DIALOGUE = "DIALOGUE"
STATE_PAUSE = "PAUSE"
STATE_ENDING = "ENDING"

ROOM_THEATER = "THEATER"
ROOM_FUTURE = "FUTURE"
ROOM_LIBRARY = "LIBRARY"

MUSIC_DEFAULT = "music/song.mp3"
MUSIC = {
    "menu": "music/menu.mp3",
    "crossroad": "music/crossroad.mp3",
    "theater": "music/theater.mp3",
    "future": "music/future.mp3",
    "library": "music/library.mp3",
    "ending": "music/ending.mp3",
}

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


def sx(x):
    return int(x)


def load_image(path, size=None):
    try:
        image = pg.image.load(path).convert_alpha()
    except Exception:
        fallback_size = size if size else (100, 100)
        image = pg.Surface(fallback_size, pg.SRCALPHA)
        image.fill((220, 30, 220, 180))
        return image

    if size:
        image = pg.transform.scale(image, size)
    return image


def load_room_image(path):
    return load_image(path)


def draw_rotated(screen, image, x, y, angle):
    rect = image.get_rect(topleft=(x, y))
    rotated_image = pg.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=rect.center)
    screen.blit(rotated_image, rotated_rect)


def smooth_step(value):
    value = clamp(value, 0, 1)
    return value * value * (3 - 2 * value)


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


def load_events():
    try:
        with open("events.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list) and data:
            return data
    except Exception:
        pass
    return []


def play_music(track_name):
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


def get_music_track(game_data):
    if game_data["state"] == STATE_MENU:
        return "menu"
    if game_data["state"] == STATE_CROSSROAD:
        return "crossroad"
    if game_data["state"] == STATE_ENDING:
        return "ending"
    if game_data["state"] in [STATE_ROOM, STATE_DIALOGUE, STATE_PAUSE]:
        if game_data["current_room"] == ROOM_THEATER:
            return "theater"
        if game_data["current_room"] == ROOM_FUTURE:
            return "future"
        if game_data["current_room"] == ROOM_LIBRARY:
            return "library"
    return "menu"


def get_room_rects(room_id):
    layout = ROOM_LAYOUT.get(room_id, ROOM_LAYOUT[ROOM_LIBRARY])
    interact = layout["interact"]
    door_rect = layout["door_rect"]
    return {
        "interact": pg.Rect(interact[0], interact[1], interact[2], interact[3]),
        "door": pg.Rect(door_rect[0], door_rect[1], door_rect[2], door_rect[3]),
        "player_spawn": (layout["player_spawn"][0], layout["player_spawn"][1]),
    }


def choose_room(last_room):
    rooms = [ROOM_THEATER, ROOM_FUTURE, ROOM_LIBRARY]
    available = []
    for room in rooms:
        if room != last_room:
            available.append(room)
    if not available:
        available = rooms
    return random.choice(available)


def choose_event_for_room(events, room_id):
    variants = []
    for event in events:
        if str(event.get("room", "")).upper() == room_id:
            variants.append(event)
    if variants:
        return random.choice(variants)
    if events:
        return random.choice(events)
    return {
        "title": "Пустая комната",
        "description": "Событие не найдено. Добавь данные в events.json.",
        "choices": [
            {"text": "Продолжить", "effects": {"humanity": 0, "logic": 0, "entropy": 0}},
            {"text": "Продолжить иначе", "effects": {"humanity": 0, "logic": 0, "entropy": 0}},
        ],
    }


def create_cloud(image):
    cloud = {
        "image": image,
        "x": random.randint(0, WIDTH),
        "y": random.randint(60, 370),
        "speed": random.uniform(0.8, 2.2),
        "wait": random.randint(0, 260),
    }
    return cloud


def update_cloud(cloud):
    if cloud["wait"] > 0:
        cloud["wait"] -= 1
        return

    cloud["x"] -= cloud["speed"]
    image_width = cloud["image"].get_width()
    if cloud["x"] < -image_width:
        cloud["wait"] = random.randint(240, 620)
        cloud["x"] = WIDTH + random.randint(20, 350)
        cloud["y"] = random.randint(60, 370)
        cloud["speed"] = random.uniform(0.8, 2.4)


def reset_run(player_rect):
    data = {
        "state": STATE_CROSSROAD,
        "prev_state": STATE_CROSSROAD,
        "stats": {"humanity": 0, "logic": 0, "entropy": 0},
        "loop_count": 0,
        "current_room": None,
        "current_event": None,
        "door_open": False,
        "room_anim": 0,
        "selected_choice": 0,
        "last_room": None,
        "ending_text": "",
    }
    player_rect.center = (WIDTH // 2, 930)
    return data


def apply_choice(game_data, choice_index):
    current_event = game_data["current_event"]
    if not current_event:
        return

    choices = current_event.get("choices", [])
    if choice_index < 0 or choice_index >= len(choices):
        return

    effects = choices[choice_index].get("effects", {})
    game_data["stats"]["humanity"] += int(effects.get("humanity", 0))
    game_data["stats"]["logic"] += int(effects.get("logic", 0))
    game_data["stats"]["entropy"] += int(effects.get("entropy", 0))
    game_data["door_open"] = True
    game_data["room_anim"] = 0
    game_data["state"] = STATE_ROOM


def get_ending_text(stats):
    h = stats["humanity"]
    l = stats["logic"]
    e = stats["entropy"]

    if e >= max(h, l) + 2:
        return "Сбой системы: хаос разрушил петлю, и мир рассыпался на части."
    if l >= h + 3 and l >= e + 2:
        return "Абсолютный прагматик: ты спас систему, но потерял все личное."
    if h >= l + 3 and h >= e + 2:
        return "Последний человек: ты спасал других, но остался в петле один."
    return "Идеальный баланс: ты не выбрал сторону, и петля замкнулась снова."


def draw_hud(screen, font, game_data):
    text = "Круг: " + str(game_data["loop_count"]) + "/" + str(MAX_LOOPS)

    panel = pg.Rect(12, 10, 140, 40)
    pg.draw.rect(screen, (10, 10, 10), panel, 0, 8)
    pg.draw.rect(screen, (150, 150, 165), panel, 2, 8)
    surf = font.render(text, True, (245, 245, 245))
    screen.blit(surf, (20, 19))




def draw_player(screen, player_image, player_rect):
    shadow = pg.Rect(player_rect.x + 8, player_rect.bottom - 12, player_rect.width - 16, 12)
    pg.draw.ellipse(screen, (20, 20, 20), shadow)
    screen.blit(player_image, player_rect)


def draw_crossroad(screen, assets, clouds, player_image, player_rect, font_small, game_data):
    cross = ROOM_LAYOUT["crossroad"]
    screen.blit(assets["cross_bg"], (cross["bg_pos"][0], cross["bg_pos"][1]))
    screen.blit(assets["cross_paths"], (cross["paths_pos"][0], cross["paths_pos"][1]))
    screen.blit(assets["cross_steps"], (cross["steps_pos"][0], cross["steps_pos"][1]))

    fountain = assets["cross_fountain"]
    fountain_pos = cross["fountain_pos"]
    screen.blit(fountain, (fountain_pos[0], fountain_pos[1]))

    left_text = font_small.render("Налево", True, (240, 240, 240))
    right_text = font_small.render("Направо", True, (240, 240, 240))
    forward_text = font_small.render("Прямо", True, (240, 240, 240))
    screen.blit(left_text, (60, 400))
    screen.blit(right_text, (860, 400))
    screen.blit(forward_text, (470, 35))

    draw_player(screen, player_image, player_rect)

    # Облака рисуем самым верхним слоем: поверх фонтана и игрока.
    for cloud in clouds:
        if cloud["wait"] <= 0:
            screen.blit(cloud["image"], (int(cloud["x"]), int(cloud["y"])))

    draw_hud(screen, font_small, game_data)
    draw_text_center(screen, "Иди по следам в туман", font_small, (240, 240, 240), 985)

def draw_theater_room(screen, assets, game_data, tick):
    layout = ROOM_LAYOUT[ROOM_THEATER]
    screen.fill((15, 15, 18))
    screen.blit(assets["theater_stage"], (layout["stage_pos"][0], layout["stage_pos"][1]))
    screen.blit(assets["theater_back_curtain"], (layout["back_curtain_pos"][0], layout["back_curtain_pos"][1]))

    if game_data["door_open"]:
        screen.blit(assets["theater_door_light"], (layout["door_light_pos"][0], layout["door_light_pos"][1]))
        screen.blit(assets["theater_door_open"], (layout["door_open_pos"][0], layout["door_open_pos"][1]))

    screen.blit(assets["theater_dummy_1"], (layout["dummy1_pos"][0], layout["dummy1_pos"][1]))
    screen.blit(assets["theater_dummy_2"], (layout["dummy2_pos"][0], layout["dummy2_pos"][1]))

    pulse = 165 + int(80 * abs(math.sin(tick * 0.04)))
    stage_light = assets["theater_spotlight"].copy()
    stage_light.set_alpha(pulse)

    light1 = assets["theater_spotlight_1"].copy()
    light1.set_alpha(pulse)
    screen.blit(light1, (layout["spotlight1_pos"][0], layout["spotlight1_pos"][1]))

    light2 = assets["theater_spotlight_2"].copy()
    light2.set_alpha(pulse)
    screen.blit(light2, (layout["spotlight2_pos"][0], layout["spotlight2_pos"][1]))

    screen.blit(assets["theater_front_curtain"], (layout["front_curtain_pos"][0], layout["front_curtain_pos"][1]))


def draw_future_room(screen, assets, game_data, tick):
    layout = ROOM_LAYOUT[ROOM_FUTURE]
    screen.blit(assets["future_room"], (layout["room_pos"][0], layout["room_pos"][1]))
    screen.blit(assets["future_wall"], (layout["wall_pos"][0], layout["wall_pos"][1]))

    if game_data["door_open"]:
        screen.blit(assets["future_door_open"], (layout["door_open_pos"][0], layout["door_open_pos"][1]))
    else:
        screen.blit(assets["future_door_locked"], (layout["door_locked_pos"][0], layout["door_locked_pos"][1]))


def draw_library_room(screen, assets, game_data, tick):
    layout = ROOM_LAYOUT[ROOM_LIBRARY]
    screen.blit(assets["library_bg"], (layout["bg_pos"][0], layout["bg_pos"][1]))

    open_progress = smooth_step(game_data["room_anim"] / 70)
    cabinet_offset = int(layout["cabinet_open_distance"] * open_progress)

    if game_data["door_open"]:
        screen.blit(assets["library_door_light"], (layout["door_light_pos"][0], layout["door_light_pos"][1]))
        screen.blit(assets["library_door_open"], (layout["door_open_pos"][0], layout["door_open_pos"][1]))
    else:
        screen.blit(assets["library_black_passage"], (layout["passage_pos"][0], layout["passage_pos"][1]))

    screen.blit(assets["library_cabinet_left"], (layout["cabinet_left_pos"][0] - cabinet_offset, layout["cabinet_left_pos"][1]))
    screen.blit(assets["library_cabinet_right"], (layout["cabinet_right_pos"][0] + cabinet_offset, layout["cabinet_right_pos"][1]))

    screen.blit(assets["library_paper_1"], (layout["paper1_pos"][0], layout["paper1_pos"][1]))
    screen.blit(assets["library_paper_2"], (layout["paper2_pos"][0], layout["paper2_pos"][1]))
    screen.blit(assets["library_paper_3"], (layout["paper3_pos"][0], layout["paper3_pos"][1]))

    screen.blit(assets["library_table"], (layout["table_pos"][0], layout["table_pos"][1]))
    screen.blit(assets["library_flower"], (layout["flower_pos"][0], layout["flower_pos"][1]))

    lamp_angle = math.sin(tick * 0.028 + math.sin(tick * 0.011) * 1.4) * 7
    lamp_angle += math.sin(tick * 0.006) * 2

    draw_rotated(screen, assets["library_lamp_light"], layout["lamp_light_pos"][0], layout["lamp_light_pos"][1], lamp_angle)
    glow = assets["library_lamp_glow"].copy()
    glow.set_alpha(120 + int(120 * abs(math.sin(tick * 0.04))))
    draw_rotated(screen, glow, layout["lamp_glow_pos"][0], layout["lamp_glow_pos"][1], lamp_angle)
    draw_rotated(screen, assets["library_lamp"], layout["lamp_pos"][0], layout["lamp_pos"][1], lamp_angle)

    screen.blit(assets["library_smoke_top"], (layout["smoke_top_pos"][0], layout["smoke_top_pos"][1]))


def draw_room(screen, assets, game_data, player_image, player_rect, font_small, tick):
    room_id = game_data["current_room"]
    room_rects = get_room_rects(room_id)

    if room_id == ROOM_THEATER:
        draw_theater_room(screen, assets, game_data, tick)
        title = "Театр"
    elif room_id == ROOM_FUTURE:
        draw_future_room(screen, assets, game_data, tick)
        title = "Футуристичный сектор"
    else:
        draw_library_room(screen, assets, game_data, tick)
        title = "Библиотека"

    interact_rect = room_rects["interact"]
    door_rect = room_rects["door"]

    if not game_data["door_open"]:
        if player_rect.colliderect(interact_rect):
            prompt = font_small.render("Нажми E", True, (255, 255, 255))
            screen.blit(prompt, (interact_rect.x + 48, interact_rect.y - 28))

    if player_rect.colliderect(door_rect) and not game_data["door_open"]:
        lock_text = font_small.render("Сначала сделай выбор", True, (255, 220, 220))
        screen.blit(lock_text, (door_rect.x - 25, door_rect.bottom + 10))

    draw_text_center(screen, title, font_small, (244, 244, 244), 68)
    draw_player(screen, player_image, player_rect)
    draw_hud(screen, font_small, game_data)


def draw_dialogue(screen, game_data, font_title, font_text, button_image):
    panel = pg.Rect(120, 160, 784, 560)
    pg.draw.rect(screen, (18, 18, 25), panel, 0, 12)
    pg.draw.rect(screen, (170, 170, 185), panel, 2, 12)
    font_button = pg.font.Font(None, 31)

    event = game_data["current_event"]
    if not event:
        return

    title = event.get("title", "Событие")
    title_surf = font_title.render(title, True, (245, 245, 245))
    screen.blit(title_surf, (panel.x + 25, panel.y + 20))

    description = event.get("description", "")
    lines = wrap_text(description, font_text, panel.width - 50)
    y = panel.y + 78
    for line in lines:
        surf = font_text.render(line, True, (220, 220, 226))
        screen.blit(surf, (panel.x + 25, y))
        y += 34

    choices = event.get("choices", [])
    for i, choice in enumerate(choices):
        button_width = 340
        button_height = 96
        if i == 0:
            rect = pg.Rect(panel.x + 35, panel.y + 355, button_width, button_height)
        else:
            rect = pg.Rect(panel.right - 35 - button_width, panel.y + 355, button_width, button_height)

        button = pg.transform.scale(button_image, (rect.width, rect.height))
        if i == game_data["selected_choice"]:
            glow_rect = pg.Rect(rect.x - 6, rect.y - 6, rect.width + 12, rect.height + 12)
            pg.draw.rect(screen, (215, 215, 180), glow_rect, 3, 10)
        screen.blit(button, rect)

        text = str(i + 1) + ". " + choice.get("text", "...")
        button_lines = wrap_text(text, font_button, rect.width - 42)
        line_height = 28
        text_y = rect.centery - (len(button_lines) * line_height) // 2
        for line in button_lines:
            surf = font_button.render(line, True, (245, 245, 245))
            screen.blit(surf, (rect.centerx - surf.get_width() // 2, text_y))
            text_y += line_height

    hint = font_text.render("1/2 или стрелки + Enter", True, (190, 190, 206))
    screen.blit(hint, (panel.x + 25, panel.bottom - 36))


def move_player(keys, player_rect):
    dx = 0
    dy = 0
    if keys[pg.K_LEFT] or keys[pg.K_a]:
        dx -= PLAYER_SPEED
    if keys[pg.K_RIGHT] or keys[pg.K_d]:
        dx += PLAYER_SPEED
    if keys[pg.K_UP] or keys[pg.K_w]:
        dy -= PLAYER_SPEED
    if keys[pg.K_DOWN] or keys[pg.K_s]:
        dy += PLAYER_SPEED

    player_rect.x += dx
    player_rect.y += dy
    player_rect.x = int(clamp(player_rect.x, 0, WIDTH - player_rect.width))
    player_rect.y = int(clamp(player_rect.y, 0, HEIGHT - player_rect.height))


def start_room(game_data, events, room_id, player_rect):
    game_data["current_room"] = room_id
    game_data["current_event"] = choose_event_for_room(events, room_id)
    game_data["door_open"] = False
    game_data["selected_choice"] = 0
    game_data["state"] = STATE_ROOM
    game_data["last_room"] = room_id

    room_rects = get_room_rects(room_id)
    player_rect.center = room_rects["player_spawn"]


def check_crossroad_transition(game_data, events, assets, player_rect):
    zones = assets["direction_zones"]
    if player_rect.colliderect(zones["left"]):
        room_id = choose_room(game_data["last_room"])
        start_room(game_data, events, room_id, player_rect)
    elif player_rect.colliderect(zones["right"]):
        room_id = choose_room(game_data["last_room"])
        start_room(game_data, events, room_id, player_rect)
    elif player_rect.colliderect(zones["forward"]):
        room_id = choose_room(game_data["last_room"])
        start_room(game_data, events, room_id, player_rect)


def try_enter_door(game_data, player_rect):
    if not game_data["door_open"]:
        return

    room_rects = get_room_rects(game_data["current_room"])
    door_rect = room_rects["door"]
    if player_rect.colliderect(door_rect):
        game_data["loop_count"] += 1
        if game_data["loop_count"] >= MAX_LOOPS:
            game_data["ending_text"] = get_ending_text(game_data["stats"])
            game_data["state"] = STATE_ENDING
            return
        game_data["state"] = STATE_CROSSROAD
        player_rect.center = (WIDTH // 2, 930)


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption(TITLE)
    clock = pg.time.Clock()

    font_small = pg.font.Font(None, 32)
    font_text = pg.font.Font(None, 38)
    font_title = pg.font.Font(None, 52)
    font_big = pg.font.Font(None, 82)

    assets = {
        "button": load_image(r"images/Button.png"),

        "cross_bg": load_image(r"images/crossroad/Каменный фон.png", (WIDTH, HEIGHT)),
        "cross_paths": load_image(r"images/crossroad/Перекрёсток.png", (WIDTH, HEIGHT)),
        "cross_steps": load_image(r"images/crossroad/Стопы.png", (WIDTH, HEIGHT)),
        "cross_fountain": load_image(r"images/crossroad/Group 79.png"),

        "theater_stage": load_room_image(r"images/room1/Сцена.png"),
        "theater_back_curtain": load_room_image(r"images/room1/Задний занавес.png"),
        "theater_front_curtain": load_room_image(r"images/room1/Занавес.png"),
        "theater_dummy_1": load_room_image(r"images/room1/Манекен1.png"),
        "theater_dummy_2": load_room_image(r"images/room1/Манекен2.png"),
        "theater_spotlight": load_room_image(r"images/room1/Свет.png"),
        "theater_spotlight_1": load_room_image(r"images/room1/Свет1.png"),
        "theater_spotlight_2": load_room_image(r"images/room1/Свет2.png"),
        "theater_door_open": load_room_image(r"images/room1/Дверь светлая.png"),
        "theater_door_light": load_room_image(r"images/room1/свет от двери.png"),

        "future_room": load_room_image(r"images/room2/Пол.png"),
        "future_wall": load_room_image(r"images/room2/Стена.png"),
        "future_door_locked": load_room_image(r"images/room2/Дверь Locked.png"),
        "future_door_open": load_room_image(r"images/room2/Дверь открытая.png"),

        "library_bg": load_room_image(r"images/room3/Фон.png"),
        "library_black_passage": load_room_image(r"images/room3/Чёрный проход.png"),
        "library_cabinet_left": load_room_image(r"images/room3/Шкаф.png"),
        "library_cabinet_right": load_room_image(r"images/room3/Шкаф-1.png"),
        "library_lamp": load_room_image(r"images/room3/Лампа.png"),
        "library_lamp_glow": load_room_image(r"images/room3/Свечение лампы.png"),
        "library_lamp_light": load_room_image(r"images/room3/Свет от лампы.png"),
        "library_table": load_room_image(r"images/room3/Стол.png"),
        "library_flower": load_room_image(r"images/room3/Цветок.png"),
        "library_paper_1": load_room_image(r"images/room3/Листок.png"),
        "library_paper_2": load_room_image(r"images/room3/Листок1.png"),
        "library_paper_3": load_room_image(r"images/room3/Листок2.png"),
        "library_smoke_top": load_room_image(r"images/room3/Черный туман сверху(дымка).png"),
        "library_door_open": load_room_image(r"images/room3/Светлая дверь.png"),
        "library_door_light": load_room_image(r"images/room3/свет от двери.png"),
    }

    cloud_images = [
        load_image(r"images/crossroad/Облако1.png"),
        load_image(r"images/crossroad/Облако2.png"),
        load_image(r"images/crossroad/Облако3.png"),
        load_image(r"images/crossroad/Облако4.png"),
        load_image(r"images/crossroad/Облако5.png"),
    ]

    clouds = []
    for i in range(4):
        clouds.append(create_cloud(cloud_images[i % len(cloud_images)]))

    cross = ROOM_LAYOUT["crossroad"]
    assets["direction_zones"] = {
        "left": pg.Rect(cross["left_zone"][0], cross["left_zone"][1], cross["left_zone"][2], cross["left_zone"][3]),
        "right": pg.Rect(cross["right_zone"][0], cross["right_zone"][1], cross["right_zone"][2], cross["right_zone"][3]),
        "forward": pg.Rect(cross["forward_zone"][0], cross["forward_zone"][1], cross["forward_zone"][2], cross["forward_zone"][3]),
    }

    player_image = load_image(r"images/character/Человек в мантии.png", (76, 128))
    player_rect = player_image.get_rect()
    game_data = reset_run(player_rect)
    game_data["state"] = STATE_MENU

    events = load_events()

    current_music = None
    tick = 0
    flag_play = True
    while flag_play:
        clock.tick(FPS)
        tick += 1

        for event in pg.event.get():
            if event.type == pg.QUIT:
                flag_play = False
                break

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if game_data["state"] == STATE_PAUSE:
                        game_data["state"] = game_data["prev_state"]
                    elif game_data["state"] in [STATE_CROSSROAD, STATE_ROOM, STATE_DIALOGUE]:
                        game_data["prev_state"] = game_data["state"]
                        game_data["state"] = STATE_PAUSE

                if game_data["state"] == STATE_MENU:
                    if event.key == pg.K_RETURN:
                        game_data = reset_run(player_rect)

                elif game_data["state"] == STATE_ROOM:
                    room_rects = get_room_rects(game_data["current_room"])
                    if event.key == pg.K_e and player_rect.colliderect(room_rects["interact"]) and not game_data["door_open"]:
                        game_data["selected_choice"] = 0
                        game_data["state"] = STATE_DIALOGUE

                elif game_data["state"] == STATE_DIALOGUE:
                    choices = game_data["current_event"].get("choices", [])
                    if event.key in [pg.K_1, pg.K_KP1] and len(choices) > 0:
                        apply_choice(game_data, 0)
                    elif event.key in [pg.K_2, pg.K_KP2] and len(choices) > 1:
                        apply_choice(game_data, 1)
                    elif event.key == pg.K_UP:
                        game_data["selected_choice"] = max(0, game_data["selected_choice"] - 1)
                    elif event.key == pg.K_DOWN:
                        game_data["selected_choice"] = min(len(choices) - 1, game_data["selected_choice"] + 1)
                    elif event.key == pg.K_RETURN and choices:
                        apply_choice(game_data, game_data["selected_choice"])

                elif game_data["state"] == STATE_ENDING:
                    if event.key == pg.K_r:
                        game_data = reset_run(player_rect)
                    elif event.key == pg.K_q:
                        flag_play = False

                elif game_data["state"] == STATE_PAUSE:
                    if event.key == pg.K_r:
                        game_data = reset_run(player_rect)

        if not flag_play:
            break

        keys = pg.key.get_pressed()
        if game_data["state"] in [STATE_CROSSROAD, STATE_ROOM]:
            move_player(keys, player_rect)

        if game_data["state"] == STATE_CROSSROAD:
            for cloud in clouds:
                update_cloud(cloud)
            check_crossroad_transition(game_data, events, assets, player_rect)
        elif game_data["state"] == STATE_ROOM:
            if game_data["door_open"] and game_data["room_anim"] < 70:
                game_data["room_anim"] += 1
            try_enter_door(game_data, player_rect)

        next_music = get_music_track(game_data)
        if next_music != current_music:
            play_music(next_music)
            current_music = next_music

        if game_data["state"] == STATE_MENU:
            screen.fill((12, 13, 20))
            draw_text_center(screen, TITLE, font_big, (245, 245, 250), 250)
            draw_text_center(screen, "Enter - начать", font_title, (220, 220, 230), 410)
            draw_text_center(screen, "WASD/Стрелки - движение", font_small, (200, 200, 212), 500)
            draw_text_center(screen, "E - выбор в комнате", font_small, (200, 200, 212), 540)
            draw_text_center(screen, "Esc - пауза", font_small, (200, 200, 212), 580)

        elif game_data["state"] == STATE_CROSSROAD:
            draw_crossroad(screen, assets, clouds, player_image, player_rect, font_small, game_data)

        elif game_data["state"] == STATE_ROOM:
            draw_room(screen, assets, game_data, player_image, player_rect, font_small, tick)

        elif game_data["state"] == STATE_DIALOGUE:
            draw_room(screen, assets, game_data, player_image, player_rect, font_small, tick)
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_dialogue(screen, game_data, font_title, font_text, assets["button"])
            draw_hud(screen, font_small, game_data)

        elif game_data["state"] == STATE_PAUSE:
            if game_data["prev_state"] == STATE_ROOM or game_data["prev_state"] == STATE_DIALOGUE:
                draw_room(screen, assets, game_data, player_image, player_rect, font_small, tick)
            else:
                draw_crossroad(screen, assets, clouds, player_image, player_rect, font_small, game_data)

            dark = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            dark.fill((0, 0, 0, 160))
            screen.blit(dark, (0, 0))
            draw_text_center(screen, "Пауза", font_big, (245, 245, 245), 350)
            draw_text_center(screen, "Esc - продолжить", font_title, (220, 220, 220), 470)
            draw_text_center(screen, "R - заново", font_title, (220, 220, 220), 530)

        elif game_data["state"] == STATE_ENDING:
            screen.fill((10, 10, 14))
            draw_text_center(screen, "Финал", font_big, (245, 245, 245), 180)

            ending_lines = wrap_text(game_data["ending_text"], font_title, 860)
            y = 360
            for line in ending_lines:
                draw_text_center(screen, line, font_title, (220, 220, 228), y)
                y += 56

            stats = game_data["stats"]
            stat_text = (
                "Humanity: "
                + str(stats["humanity"])
                + " | Logic: "
                + str(stats["logic"])
                + " | Entropy: "
                + str(stats["entropy"])
            )
            draw_text_center(screen, stat_text, font_small, (200, 200, 210), 690)
            draw_text_center(screen, "R - заново    Q - выход", font_title, (220, 220, 230), 810)

        pg.display.update()

    pg.quit()


if __name__ == "__main__":
    main()
