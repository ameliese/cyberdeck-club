## Fonts konvertieren
Um eine bestimmte Schrift Schrift mit dem Setup ESP32+ SSD1306 OLED zu nutzen, wandelt die Schrift vorher um. 

https://github.com/peterhinch/micropython-font-to-py

## Kurzanleitung
Schrift umwandeln ohne Umlaute/Sonderzeichen, im Font-Ordner (Terminal):
```bash
pip install font_to_py
font_to_py deinfont.otf 16 deinfont16.py #(16 ist hier die Schriftgröße)
```
– auf ESP speichern: `ssd1306.py`,  `ssd1306_setup.py`, `writer.py`, `deinfont.py`

– dann testen mit Testfile: `Test_eigener-Font.py`

Weitere Optionen + Infos, s. https://github.com/peterhinch/micropython-font-to-py

## ESP+OLED taugliche Fonts und mehr
https://github.com/easytarget/microPyEZfonts
