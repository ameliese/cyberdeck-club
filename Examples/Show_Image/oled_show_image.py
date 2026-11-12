from machine import Pin, I2C
import ssd1306
import framebuf
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

FRAME_COUNT = 6 # so viele Bilder sollen gezeigt werden 
DELAY_MS = 800 # so lange (in Millisekunden) soll ein Bild gezeigt werden

def load_frame(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return framebuf.FrameBuffer(bytearray(data), 128, 64, framebuf.MONO_HLSB)

frames = [load_frame(f"frame{i}.bin") for i in range(FRAME_COUNT)]

idx = 0
while True:
    display.fill(0)
    display.blit(frames[idx], 0, 0)
    display.show()
    idx = (idx + 1) % FRAME_COUNT
    time.sleep_ms(DELAY_MS)