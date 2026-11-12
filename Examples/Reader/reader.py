from machine import Pin, I2C
import ssd1306
import time
import gc

# --- Hardware ---
W, H = 128, 64
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(W, H, i2c, addr=0x3C)

# Taster gegen GND, interner Pull-up: gedrueckt = 0
btn_up = Pin(4, Pin.IN, Pin.PULL_UP)     # scrollt nach oben (zurueck)
btn_down = Pin(5, Pin.IN, Pin.PULL_UP)   # scrollt nach unten (weiter)

# --- Einstellungen ---
TEXT_FILE = "luddites.txt"   # Textdatei auf dem ESP32 (UTF-8)
CHARS = 15               # Zeichen pro Zeile (8px-Schrift; rechts bleibt Platz fuer Scrollbalken)
ROWS = 7                 # Zeilen pro Bildschirm (64px / 8px)
REPEAT_DELAY_MS = 300    # so lange gedrueckt halten, bis Dauer-Scrollen startet
REPEAT_STEP_MS = 80      # Abstand zwischen Zeilen beim Dauer-Scrollen

FALLBACK_TEXT = (
    "Keine text.txt auf dem ESP32 gefunden.\n\n"
    "Lege eine Datei namens text.txt (UTF-8) in das Hauptverzeichnis "
    "des ESP32 und starte neu. Mit den zwei Tastern scrollst du hoch "
    "und runter."
)

# Die eingebaute 8x8-Schrift kennt nur ASCII -> Sonderzeichen ersetzen
REPLACE = (
    ("ä", "ae"), ("ö", "oe"), ("ü", "ue"),
    ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue"), ("ß", "ss"),
    ("–", "-"), ("—", "-"), ("„", '"'), ("“", '"'), ("”", '"'),
    ("‚", "'"), ("‘", "'"), ("’", "'"), ("…", "..."), ("€", "EUR"),
)


def to_ascii(s):
    s = s.replace("\r", "")
    for a, b in REPLACE:
        s = s.replace(a, b)
    return "".join(c if ord(c) < 128 else "?" for c in s)


def wrap(text):
    """Bricht Text an Wortgrenzen auf CHARS Zeichen um. Leerzeilen bleiben erhalten."""
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            while len(word) > CHARS:                 # zu langes Wort trennen
                if line:
                    lines.append(line)
                    line = ""
                lines.append(word[:CHARS - 1] + "-")
                word = word[CHARS - 1:]
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= CHARS:
                line += " " + word
            else:
                lines.append(line)
                line = word
        lines.append(line)                           # auch leere Absaetze -> Leerzeile
    return lines


# --- Text laden ---
try:
    with open(TEXT_FILE, "r") as f:
        raw = f.read()
except OSError:
    raw = FALLBACK_TEXT

lines = wrap(to_ascii(raw).rstrip())
del raw
gc.collect()

max_top = max(0, len(lines) - ROWS)


def draw(top):
    oled.fill(0)
    for i in range(ROWS):
        n = top + i
        if n < len(lines):
            oled.text(lines[n], 0, i * 8, 1)
    if len(lines) > ROWS:                            # Scrollbalken rechts
        bar_h = max(4, H * ROWS // len(lines))
        y = (H - bar_h) * top // max_top
        oled.fill_rect(126, y, 2, bar_h, 1)
    oled.show()


top = 0
draw(top)
held_since = None
last_step = 0

while True:
    now = time.ticks_ms()
    d = (btn_down.value() == 0) - (btn_up.value() == 0)   # +1 = runter, -1 = hoch, 0 = nichts/beide

    if d != 0:
        if held_since is None:                       # frischer Tastendruck -> sofort 1 Zeile
            held_since = now
            step = True
        else:                                        # gehalten -> nach Verzoegerung Dauer-Scrollen
            step = (time.ticks_diff(now, held_since) > REPEAT_DELAY_MS
                    and time.ticks_diff(now, last_step) > REPEAT_STEP_MS)
        if step:
            last_step = now
            new_top = min(max(top + d, 0), max_top)
            if new_top != top:
                top = new_top
                draw(top)
    else:
        held_since = None

    time.sleep_ms(10)
