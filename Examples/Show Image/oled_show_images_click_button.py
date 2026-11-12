from machine import Pin, I2C
import ssd1306
import framebuf
import os
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

btn_next = Pin(4, Pin.IN, Pin.PULL_UP) # nächstes Bild: Taster an Pin 4
btn_prev = Pin(5, Pin.IN, Pin.PULL_UP) # vorheriges Bild: Taster an Pin 5
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
