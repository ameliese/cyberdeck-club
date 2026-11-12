# ACHTUNG, BUGGY

from machine import Pin, I2C, disable_irq, enable_irq
import ssd1306
import time
import random
from encoder import Encoder

# --- Hardware ---
W, H = 128, 64
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(W, H, i2c, addr=0x3C)

# --- Drehgeber (Rotary Encoder) ---
# Verkabelung: + -> 3V3 (nicht 5V!), GND -> GND, CLK -> 18, DT -> 19
ENC_CLK = 18
ENC_DT = 19
STEPS_PER_DETENT = 1   # Signalwechsel pro Rastung: meist 4 (KY-040), manche Module 2 oder 1
INVERT = False         # True, wenn Drehen im Uhrzeigersinn den Schlaeger nach oben statt nach unten bewegt

# Zustandstabelle fuer Quadratur-Dekodierung: Index = (alter Zustand << 2) | neuer Zustand
_TABLE = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)





enc = Encoder(ENC_CLK, ENC_DT, INVERT)

# --- Spiel-Einstellungen (zum Tunen) ---
PAD_W, PAD_H = 3, 14      # Schlaeger-Groesse
PAD_STEP = 5              # Pixel, die sich der Schlaeger pro Rastung bewegt
AI_SPEED = 2              # Computer-Geschwindigkeit (kleiner = leichter)
BALL = 3                  # Ballgroesse
BALL_SPEED_START = 2.0    # Start-Geschwindigkeit in x
BALL_SPEED_MAX = 4.5
WIN_SCORE = 5
FRAME_MS = 30

PLAYER_X = 2
AI_X = W - 2 - PAD_W


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def draw(px, ay_, bx, by, ps, ai_s):
    oled.fill(0)
    for y in range(0, H, 6):                    # gestrichelte Mittellinie
        oled.vline(W // 2, y, 3, 1)
    oled.text(str(ps), W // 2 - 24, 2, 1)       # Punktestand
    oled.text(str(ai_s), W // 2 + 16, 2, 1)
    oled.fill_rect(PLAYER_X, int(px), PAD_W, PAD_H, 1)
    oled.fill_rect(AI_X, int(ay_), PAD_W, PAD_H, 1)
    oled.fill_rect(int(bx), int(by), BALL, BALL, 1)
    oled.show()


def serve(direction):
    # Ball in die Mitte, Richtung: 1 = nach rechts, -1 = nach links
    vy = random.choice((-1.5, -1.0, 1.0, 1.5))
    return W / 2, H / 2, BALL_SPEED_START * direction, vy


def play():
    py = ay = (H - PAD_H) / 2
    ps = ai_s = 0
    bx, by, vx, vy = serve(random.choice((-1, 1)))
    draw(py, ay, bx, by, ps, ai_s)
    time.sleep_ms(800)

    while ps < WIN_SCORE and ai_s < WIN_SCORE:
        t0 = time.ticks_ms()

        # --- Eingabe ---
        py = clamp(py + enc.read() * PAD_STEP, 0, H - PAD_H)

        # --- Computer-Schlaeger ---
        # Folgt dem Ball nur, wenn er auf ihn zukommt; sonst zurueck zur Mitte
        target = (by + BALL / 2) if vx > 0 else H / 2
        center = ay + PAD_H / 2
        if abs(target - center) > AI_SPEED:
            ay += AI_SPEED if target > center else -AI_SPEED
        ay = clamp(ay, 0, H - PAD_H)

        # --- Ball bewegen ---
        bx += vx
        by += vy

        # Oben/unten abprallen
        if by <= 0:
            by = 0
            vy = -vy
        elif by + BALL >= H:
            by = H - BALL
            vy = -vy

        # Spieler-Schlaeger (links)
        if vx < 0 and bx <= PLAYER_X + PAD_W and bx + BALL >= PLAYER_X \
                and by + BALL >= py and by <= py + PAD_H:
            bx = PLAYER_X + PAD_W
            vx = min(-vx * 1.05, BALL_SPEED_MAX)
            vy = ((by + BALL / 2) - (py + PAD_H / 2)) / (PAD_H / 2) * 2.5

        # Computer-Schlaeger (rechts)
        elif vx > 0 and bx + BALL >= AI_X and bx <= AI_X + PAD_W \
                and by + BALL >= ay and by <= ay + PAD_H:
            bx = AI_X - BALL
            vx = -min(vx * 1.05, BALL_SPEED_MAX)
            vy = ((by + BALL / 2) - (ay + PAD_H / 2)) / (PAD_H / 2) * 2.5

        # --- Punkt? ---
        if bx + BALL < 0:                        # links raus -> Computer punktet
            ai_s += 1
            bx, by, vx, vy = serve(-1)           # Aufschlag zum Verlierer
            draw(py, ay, bx, by, ps, ai_s)
            time.sleep_ms(800)
        elif bx > W:                             # rechts raus -> Spieler punktet
            ps += 1
            bx, by, vx, vy = serve(1)
            draw(py, ay, bx, by, ps, ai_s)
            time.sleep_ms(800)

        draw(py, ay, bx, by, ps, ai_s)

        # Framerate halten
        dt = time.ticks_diff(time.ticks_ms(), t0)
        if dt < FRAME_MS:
            time.sleep_ms(FRAME_MS - dt)

    return ps > ai_s                             # True = Spieler hat gewonnen


def wait_for_turn():
    enc.read()                                  # alte Drehung verwerfen
    while enc.read() == 0:                      # auf neue Drehung warten
        time.sleep_ms(20)


while True:
    won = play()
    oled.fill(0)
    oled.text("YOU WIN!" if won else "COMPUTER WINS", 16 if not won else 32, 16, 1)
    oled.text("Drehen=Neustart", 4, 40, 1)
    oled.show()
    wait_for_turn()