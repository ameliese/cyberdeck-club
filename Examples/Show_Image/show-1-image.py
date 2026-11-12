from machine import Pin, I2C
import ssd1306, framebuf

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

with open('frame0.bin', 'rb') as f: #frame muss vorher manuell auf den esp geladen werden (Dateien > Rechtsklick > Upload nach)
    data = f.read()
buf = framebuf.FrameBuffer(bytearray(data), 128, 64, framebuf.MONO_HLSB)

display.fill(0)
display.blit(buf, 0, 0)
display.show()