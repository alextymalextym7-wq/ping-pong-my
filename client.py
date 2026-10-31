from pygame import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")
# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 55555)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)
# --- ЗОБРАЖЕННЯ ----
bg = image.load("background.png")  # Вкажіть назву вашого файлу
bg = transform.scale(bg, (WIDTH, HEIGHT))

paddle1_img = image.load("paddle1.png")
paddle1_img = transform.scale(paddle1_img, (40, 140))

paddle2_img = image.load("paddle2.png")
paddle2_img = transform.scale(paddle2_img, (40, 140))

ball_img = image.load("ball.png")
ball_img = transform.scale(ball_img, (50, 50))

ball_skins = [ball_img]
current_skin_index = 0

# 4. МЕНЮ ТА КНОПКИ
state = "MENU"

play_btn = Rect(300, 200, 200, 50)
settings_btn = Rect(300, 270, 200, 50)
exit_btn = Rect(300, 340, 200, 50)

skin_btn = Rect(250, 220, 300, 50)
back_btn = Rect(300, 380, 200, 50)


# ПРОСТА ФУНКЦИЯ ДЛЯ МАЛЮВАННЯ КНОПОК
def draw_button(rect, text, color):
    draw.rect(screen, color, rect)
    btn_text = font_main.render(text, True, (255, 255, 255))
    screen.blit(btn_text, btn_text.get_rect(center=rect.center))
# --- МЕНЮ ТА КНОПКИ ---


# --- ЗВУКИ ---

# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    # Обробка дій гравця (мишка та закриття вікна)
    for e in event.get():
        if e.type == QUIT:
            exit()

        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            if state == "MENU":
                if play_btn.collidepoint(e.pos):
                    state = "GAME"
                if settings_btn.collidepoint(e.pos):
                    state = "SETTINGS"
                if exit_btn.collidepoint(e.pos):
                    exit()

            elif state == "SETTINGS":
                if skin_btn.collidepoint(e.pos):
                    current_skin_index = (current_skin_index + 1) % len(
                        ball_skins
                    )
                if back_btn.collidepoint(e.pos):
                    state = "MENU"

    # --- 1. ЕКРАН "ГОЛОВНЕ МЕНЮ" ---
    if state == "MENU":
        screen.blit(bg, (0, 0))
        draw_button(play_btn, "Грати", (50, 150, 50))
        draw_button(settings_btn, "Налаштування", (50, 50, 150))
        draw_button(exit_btn, "Вихід", (150, 50, 50))

    # --- 2. ЕКРАН "НАЛАШТУВАННЯ" ---
    elif state == "SETTINGS":
        screen.blit(bg, (0, 0))
        draw_button(skin_btn, "Змінити скін м'яча", (70, 70, 70))
        draw_button(back_btn, "Назад", (150, 50, 50))
        screen.blit(ball_skins[current_skin_index], (570, 220))

    # --- 3. ЕКРАН "ГРА" ---
    elif state == "GAME":
        # Зворотний відлік
        if "countdown" in game_state and game_state["countdown"] > 0:
            screen.fill((0, 0, 0))
            countdown_text = font_win.render(
                str(game_state["countdown"]), True, (255, 255, 255)
            )
            screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))

        # Переможець
        elif "winner" in game_state and game_state["winner"] is not None:
            screen.fill((20, 20, 20))
            if you_winner is None:
                you_winner = game_state["winner"] == my_id

            if you_winner:
                win_text = font_win.render("Ти переміг!", True, (255, 215, 0))
            else:
                win_text = font_win.render(
                    "Пощастить наступним разом!", True, (255, 215, 0)
                )

            screen.blit(
                win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            )

        # Процес гри
        elif game_state and "paddles" in game_state:
            screen.blit(bg, (0, 0))
            screen.blit(paddle1_img, (10, game_state["paddles"]["0"]))
            screen.blit(paddle2_img, (WIDTH - 50, game_state["paddles"]["1"]))
            screen.blit(
                ball_skins[current_skin_index],
                (game_state["ball"]["x"] - 25, game_state["ball"]["y"] - 25),
            )

            score_text = font_main.render(
                f"{game_state['scores'][0]} : {game_state['scores'][1]}",
                True,
                (255, 255, 255),
            )
            screen.blit(score_text, (WIDTH // 2 - 25, 20))

        # Чекаємо на 2-го гравця
        else:
            screen.blit(bg, (0, 0))
            wating_text = font_main.render(
                "Очікування гравців...", True, (255, 255, 255)
            )
            screen.blit(wating_text, (WIDTH // 2 - 120, HEIGHT // 2))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
