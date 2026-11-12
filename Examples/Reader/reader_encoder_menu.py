# Reader mit Drehknopf + Menü: Drehen = Scrollen, Drücken = im Menü: Auswählen, im Text: Nach oben springen, Drücken + gegen den UZS drehen = zurück zum Menü, Schrift = automatisch


import os
from machine import Pin, I2C
from encoder import Encoder
import ssd1306
import time
import gc

# --- Hardware ---
W, H = 128, 64
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(W, H, i2c, addr=0x3C)

# --- Drehgeber (Rotary Encoder) ---
# Verkabelung: + -> 3V3 (nicht 5V!), GND -> GND, CLK -> 18, DT -> 19
ENC_CLK = 18
ENC_DT = 19
ENC_SW = 23
STEPS_PER_DETENT = 4   # Signalwechsel pro Rastung: meist 4 (KY-040), manche Module 2 oder 1
INVERT = True         # Drehrichtung

enc = Encoder(ENC_CLK, ENC_DT, INVERT, STEPS_PER_DETENT, sw=ENC_SW)

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

BACK_DIR = -1            # Drehrichtung fuer "zurueck zum Menue" (gedrueckt drehen)
MENU_ROWS = 8


def list_files():
    fs = [f for f in os.listdir() if f.lower().endswith(".txt")]
    fs.sort()
    return fs


def load(fname):
    global lines, max_top
    try:
        with open(fname, "r") as f:
            raw = f.read()
    except OSError:
        raw = FALLBACK_TEXT
    lines = None
    gc.collect()
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


def draw_menu(files, sel, first):
    oled.fill(0)
    for i in range(MENU_ROWS):
        n = first + i
        if n >= len(files):
            break
        name = to_ascii(files[n][:-4])[:CHARS]
        if n == sel:
            oled.fill_rect(0, i * 8, 126, 8, 1)      # weisser Balken
            oled.text(name, 0, i * 8, 0)
        else:
            oled.text(name, 0, i * 8, 1)
    if len(files) > MENU_ROWS:                       # Scrollbalken
        bar_h = max(4, H * MENU_ROWS // len(files))
        y = (H - bar_h) * first // (len(files) - MENU_ROWS)
        oled.fill_rect(126, y, 2, bar_h, 1)
    oled.show()


def menu():
    files = list_files()
    if not files:
        oled.fill(0)
        oled.text("Keine .txt", 0, 0, 1)
        oled.text("gefunden", 0, 8, 1)
        oled.show()
        while True:
            time.sleep_ms(1000)
    sel = 0
    first = 0
    draw_menu(files, sel, first)
    while True:
        d = enc.read()
        if d:
            new = min(max(sel + d, 0), len(files) - 1)
            if new != sel:
                sel = new
                if sel < first:
                    first = sel
                elif sel >= first + MENU_ROWS:
                    first = sel - MENU_ROWS + 1
                draw_menu(files, sel, first)
        if enc.clicked():
            return files[sel]
        time.sleep_ms(5)


def reader():
    top = 0
    draw(top)
    while True:
        d = enc.read()
        if d:
            if enc.pressed():
                if d * BACK_DIR > 0:                 # gedrueckt + Gegenrichtung -> Menue
                    return
            else:
                new_top = min(max(top + d, 0), max_top)
                if new_top != top:
                    top = new_top
                    draw(top)
        if enc.clicked():                            # kurz klicken -> nach oben
            top = 0
            draw(top)
        time.sleep_ms(5)


lines = []
max_top = 0

while True:
    fname = menu()
    load(fname)
    reader()
    while enc.pressed():                             # Taste loslassen abwarten
        time.sleep_ms(10)
    enc.clicked()                                    # Rest-Klick verwerfen
    enc.read()