from machine import Pin, SoftI2C
import ssd1306, framebuf
from writer import Writer
import apfel40   # Dateiname deiner konvertierten Schrift, ohne .py

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

wri = Writer(oled, apfel40)
Writer.set_textpos(oled, 0, 0)   # Zeile, Spalte
wri.printstring('Hallo ESP32')
oled.show()