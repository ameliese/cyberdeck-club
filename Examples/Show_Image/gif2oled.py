#!/usr/bin/env python3
"""
gif2oled.py — Konvertiert ein GIF (oder MP4) in Frames für 128x64 SSD1306 OLEDs.

Voraussetzungen (auf dem PC, NICHT auf dem ESP32):
    pip install pillow numpy
    # nur für MP4 zusaetzlich:
    pip install opencv-python

Nutzung:
    python gif2oled.py animation.gif  --out out_folder --fps 8
    python gif2oled.py animation.mp4  --out out_folder --fps 8

Ergebnis im Output-Ordner:
    frame0.bin, frame1.bin, ...   (rohe MONO_HLSB-Bytes, je 1024 Byte)
    main.py                       (fertiges Abspiel-Skript fuer den ESP32)

Danach: kompletten Inhalt des Output-Ordners auf den ESP32 hochladen (Thonny).
"""

import argparse
import os
import sys

from PIL import Image, ImageSequence
import numpy as np

WIDTH, HEIGHT = 128, 64


def frame_to_mono_hlsb(img: Image.Image, threshold: int = 128, dither: bool = True) -> bytes:
    """Wandelt ein PIL-Image in MONO_HLSB-Bytes um (das Format, das
    framebuf.FrameBuffer(..., framebuf.MONO_HLSB) erwartet).

    MONO_HLSB: 1 Bit pro Pixel, MSB zuerst, Bytes zeilenweise, jede Zeile
    auf ein Vielfaches von 8 Pixeln aufgefuellt (bei 128 Breite passt das exakt).
    """
    # Auf Zielgroesse bringen, Seitenverhaeltnis wird NICHT automatisch erhalten
    # (bei Bedarf vorher selbst zuschneiden/anpassen)
    img = img.convert("L").resize((WIDTH, HEIGHT))

    if dither:
        # Floyd-Steinberg-Dithering: sieht bei Fotos/Verlaeufen deutlich besser aus
        # als einfaches Schwarz/Weiss-Abschneiden
        img = img.convert("1")  # Pillow's eingebautes 1-Bit-Dithering
        arr = np.array(img, dtype=np.uint8)  # 0 oder 255
        bits = (arr > 0).astype(np.uint8)
    else:
        arr = np.array(img, dtype=np.uint8)
        bits = (arr >= threshold).astype(np.uint8)

    # bits hat Shape (HEIGHT, WIDTH), Werte 0/1
    # In Bytes packen: 8 Pixel pro Byte, MSB = am weitesten links
    packed = np.packbits(bits, axis=1)  # (HEIGHT, WIDTH/8) da WIDTH=128 -> 16 Byte/Zeile
    return packed.tobytes()


def load_frames_gif(path):
    im = Image.open(path)
    frames = []
    durations = []
    for frame in ImageSequence.Iterator(im):
        frames.append(frame.convert("RGB"))
        durations.append(frame.info.get("duration", 100))  # ms
    return frames, durations


def load_frames_mp4(path, fps):
    import cv2  # nur hier importieren, damit GIF-Nutzung ohne opencv funktioniert
    cap = cv2.VideoCapture(path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, round(src_fps / fps))
    frames = []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % step == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb))
        i += 1
    cap.release()
    durations = [int(1000 / fps)] * len(frames)
    return frames, durations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Pfad zu .gif, .mp4, einem Einzelbild, oder einem ORDNER mit mehreren Bildern")
    ap.add_argument("--out", default="oled_out", help="Ausgabeordner")
    ap.add_argument("--fps", type=int, default=8, help="Ziel-Framerate (nur fuer MP4 / Anzeige-Timing)")
    ap.add_argument("--no-dither", action="store_true", help="Dithering deaktivieren (harte Schwelle statt Floyd-Steinberg)")
    ap.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270], help="Bild um Grad drehen (im Uhrzeigersinn)")
    ap.add_argument("--max-frames", type=int, default=0, help="Optional: Frames begrenzen (0 = alle)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
    is_gallery = False    # mehrere Einzelbilder aus einem Ordner (fuer Taster-Navigation)
    is_still_image = False  # einzelnes Standbild (kein Loop noetig)

    if os.path.isdir(args.input):
        # Ordner-Modus: alle Bilder darin, alphabetisch sortiert, werden zu
        # frame0.bin, frame1.bin, ... - passend zur Taster-Navigation (main.py
        # sucht dort automatisch alle frameN.bin und blaettert durch)
        files = sorted(
            f for f in os.listdir(args.input)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS
        )
        if not files:
            sys.exit(f"Keine Bilder ({', '.join(IMAGE_EXTS)}) in '{args.input}' gefunden")
        frames = [Image.open(os.path.join(args.input, f)).convert("RGB") for f in files]
        durations = [0] * len(frames)
        is_gallery = True
        print("Gefundene Bilder (in dieser Reihenfolge -> frame0.bin, frame1.bin, ...):")
        for i, f in enumerate(files):
            print(f"  frame{i}.bin  <-  {f}")
    else:
        ext = os.path.splitext(args.input)[1].lower()
        is_still_image = ext in IMAGE_EXTS

        if ext == ".gif":
            frames, durations = load_frames_gif(args.input)
        elif ext in (".mp4", ".mov", ".avi", ".mkv"):
            frames, durations = load_frames_mp4(args.input, args.fps)
        elif is_still_image:
            frames = [Image.open(args.input).convert("RGB")]
            durations = [0]
        else:
            sys.exit(f"Nicht unterstuetztes Format: {ext}")

    if args.max_frames:
        frames = frames[: args.max_frames]
        durations = durations[: args.max_frames]

    if not frames:
        sys.exit("Keine Frames gefunden.")

    for i, frame in enumerate(frames):
        if args.rotate:
            # PIL dreht mathematisch gegen den Uhrzeigersinn -> negieren fuer "im Uhrzeigersinn"
            frame = frame.rotate(-args.rotate, expand=True)
        data = frame_to_mono_hlsb(frame, dither=not args.no_dither)
        with open(os.path.join(args.out, f"frame{i}.bin"), "wb") as f:
            f.write(data)

    if is_gallery:
        # Mehrere Einzelbilder: main.py mit zwei Tastern zum Vor-/Zurueckblaettern
        # (GPIO 4 = vorwaerts, GPIO 5 = zurueck, jeweils gegen GND, interner Pull-up)
        main_py = '''from machine import Pin, I2C
import ssd1306
import framebuf
import os
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

btn_next = Pin(4, Pin.IN, Pin.PULL_UP)
btn_prev = Pin(5, Pin.IN, Pin.PULL_UP)
DEBOUNCE_MS = 200

def find_frame_files():
    files = [f for f in os.listdir() if f.startswith("frame") and f.endswith(".bin")]
    files.sort(key=lambda f: int(f[len("frame"):-len(".bin")]))
    return files

frame_files = find_frame_files()
if not frame_files:
    raise Exception("Keine frameN.bin Dateien gefunden")

def load_frame(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return framebuf.FrameBuffer(bytearray(data), 128, 64, framebuf.MONO_HLSB)

def show(idx):
    buf = load_frame(frame_files[idx])
    display.fill(0)
    display.blit(buf, 0, 0)
    display.show()

idx = 0
show(idx)
last_press_time = 0

while True:
    now = time.ticks_ms()
    if btn_next.value() == 0 and time.ticks_diff(now, last_press_time) > DEBOUNCE_MS:
        idx = (idx + 1) % len(frame_files)
        show(idx)
        last_press_time = now
    elif btn_prev.value() == 0 and time.ticks_diff(now, last_press_time) > DEBOUNCE_MS:
        idx = (idx - 1) % len(frame_files)
        show(idx)
        last_press_time = now
    time.sleep_ms(20)
'''
    elif is_still_image:
        # Einzelbild: kein Loop, kein Timing noetig - einmal zeichnen reicht
        main_py = '''from machine import Pin, I2C
import ssd1306
import framebuf

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

with open("frame0.bin", "rb") as f:
    data = f.read()
buf = framebuf.FrameBuffer(bytearray(data), 128, 64, framebuf.MONO_HLSB)

display.fill(0)
display.blit(buf, 0, 0)
display.show()
'''
    else:
        avg_ms = sum(durations) / len(durations)
        main_py = f'''from machine import Pin, I2C
import ssd1306
import framebuf
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

FRAME_COUNT = {len(frames)}
DELAY_MS = {int(avg_ms)}

def load_frame(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return framebuf.FrameBuffer(bytearray(data), 128, 64, framebuf.MONO_HLSB)

frames = [load_frame(f"frame{{i}}.bin") for i in range(FRAME_COUNT)]

idx = 0
while True:
    display.fill(0)
    display.blit(frames[idx], 0, 0)
    display.show()
    idx = (idx + 1) % FRAME_COUNT
    time.sleep_ms(DELAY_MS)
'''
    with open(os.path.join(args.out, "main.py"), "w") as f:
        f.write(main_py)

    total_kb = sum(os.path.getsize(os.path.join(args.out, f"frame{i}.bin")) for i in range(len(frames))) / 1024
    print(f"{len(frames)} Frame(s) erzeugt in '{args.out}/'")
    print(f"Gesamtgroesse: {total_kb:.1f} KB (ESP32-Flash beachten: meist 4 MB, davon einiges fuer Firmware belegt)")
    if is_gallery:
        print("Taster-Navigation: GPIO 4 = vorwaerts, GPIO 5 = zurueck (gegen GND)")
    elif not is_still_image:
        print(f"Timing: ~{int(avg_ms)}ms pro Frame")


if __name__ == "__main__":
    main()
