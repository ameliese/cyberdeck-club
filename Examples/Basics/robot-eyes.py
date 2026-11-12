# 0x1306.dev · animation: eyes_look_left · robot_eyes · 125ms
import machine, ssd1306, time

i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def fill_round_rect(x, y, w, h, r, c=1):
    if r < 1: r = 1
    oled.fill_rect(x + r, y, w - 2*r, h, c)
    oled.fill_rect(x, y + r, r, h - 2*r, c)
    oled.fill_rect(x + w - r, y + r, r, h - 2*r, c)
    oled.ellipse(x + r,     y + r,     r, r, c, 0b0001)
    oled.ellipse(x + w - r, y + r,     r, r, c, 0b0010)
    oled.ellipse(x + r,     y + h - r, r, r, c, 0b0100)
    oled.ellipse(x + w - r, y + h - r, r, r, c, 0b1000)

def draw_eyes(lx, ly, lw, lh, lr, rx, ry, rw, rh, rr):
    fill_round_rect(lx - lw//2, ly - lh//2, lw, lh, lr)
    fill_round_rect(rx - rw//2, ry - rh//2, rw, rh, rr)

def draw_frame(frame):
    oled.fill(0)
    ox = [0, -4, -8, -10, -8, -4][frame % 8]
    draw_eyes(32, 32, 38, 28, 8, 96, 32, 38, 28, 8)
    oled.ellipse(32 + ox, 32, 8, 8, 0, True)
    oled.ellipse(96 + ox, 32, 8, 8, 0, True)
    oled.show()
    oled.show()

while True:
    for i in range(6):
        draw_frame(i)
        time.sleep_ms(125)