from machine import Pin, I2C
from encoder import Encoder
import ssd1306
import time
import gc
from writer import Writer
import ezFBfont_6x12_ascii_10          # <-- Name deiner konvertierten Schrift (ohne .py)

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

# --- Schrift ---
wri = Writer(oled, ezFBfont_6x12_ascii_10, verbose=False)
wri.set_clip(True, True, False)          # kein automatischer Umbruch, ueberstehendes wird abgeschnitten

FONT_HAS_UMLAUTS = False   # True, wenn du aeoeue/AeOeUe/ss mit in die Schrift konvertiert hast
LINE_GAP = 1               # zusaetzlicher Abstand zwischen den Zeilen in Pixeln

LINE_H = ezFBfont_6x12_ascii_10.height() + LINE_GAP
ROWS = H // LINE_H         # Zeilen pro Bildschirm, ergibt sich aus der Schrifthoehe
TEXT_W = 123               # nutzbare Breite in Pixeln (rechts bleibt Platz fuer den Scrollbalken)

# --- Einstellungen ---
TEXT_FILE = "luddites.txt"   # Textdatei auf dem ESP32 (UTF-8)

FALLBACK_TEXT = (
    "Keine text.txt auf dem ESP32 gefunden.\n\n"
    "Lege eine Datei namens text.txt (UTF-8) in das Hauptverzeichnis "
    "des ESP32 und starte neu. Mit den zwei Tastern scrollst du hoch "
    "und runter."
)

# Typografische Zeichen, die in kaum einer Schrift enthalten sind
REPLACE = (
    ("–", "-"), ("—", "-"), ("„", '"'), ("“", '"'), ("”", '"'),
    ("‚", "'"), ("‘", "'"), ("’", "'"), ("…", "..."), ("€", "EUR"),
)
# Nur ersetzen, wenn die Schrift keine Umlaute hat
REPLACE_UMLAUTS = (
    ("ä", "ae"), ("ö", "oe"), ("ü", "ue"),
    ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue"), ("ß", "ss"),
)
UMLAUTS = "äöüÄÖÜß"


def clean(s):
    s = s.replace("\r", "")
    for a, b in REPLACE:
        s = s.replace(a, b)
    if not FONT_HAS_UMLAUTS:
        for a, b in REPLACE_UMLAUTS:
            s = s.replace(a, b)
    ok = UMLAUTS if FONT_HAS_UMLAUTS else ""
    return "".join(c if (ord(c) < 128 or c in ok) else "?" for c in s)


def width(s):
    return wri.stringlen(s)


def wrap(text):
    """Bricht Text an Wortgrenzen auf TEXT_W Pixel um. Leerzeilen bleiben erhalten."""
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            while width(word) > TEXT_W:              # zu langes Wort trennen
                if line:
                    lines.append(line)
                    line = ""
                n = len(word)
                while n > 1 and width(word[:n] + "-") > TEXT_W:
                    n -= 1
                lines.append(word[:n] + "-")
                word = word[n:]
            if not line:
                line = word
            elif width(line + " " + word) <= TEXT_W:
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

lines = wrap(clean(raw).rstrip())
del raw
gc.collect()

max_top = max(0, len(lines) - ROWS)


def draw(top):
    oled.fill(0)
    for i in range(ROWS):
        n = top + i
        if n < len(lines):
            Writer.set_textpos(oled, i * LINE_H, 0)  # (Zeile in Pixeln, Spalte in Pixeln)
            wri.printstring(lines[n])
    if len(lines) > ROWS:                            # Scrollbalken rechts
        bar_h = max(4, H * ROWS // len(lines))
        y = (H - bar_h) * top // max_top
        oled.fill_rect(126, y, 2, bar_h, 1)
    oled.show()


top = 0
draw(top)

while True:
    d = enc.read()
    if d:
        step = ROWS if enc.pressed() else 1 # drehen scrollt 1 Zeile, gedrückt halten und drehen scrollt 1 Seite
        new_top = min(max(top + d * step, 0), max_top)
        if new_top != top:
            top = new_top
            draw(top)    
    if enc.clicked(): # kurz klicken, um nach oben zu springen
        top = 0
        draw(top)
    time.sleep_ms(5)
