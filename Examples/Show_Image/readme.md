## GIF2OLED 
(png, jpeg, mp4 geht auch)

## Installieren 
(im Terminal, nicht auf dem ESP32): `pip install pillow numpy`

nur für MP4 zusaetzlich: `pip install opencv-python`

## Benutzen
gif2oled.py muss im gleichen Ordner wie das Bild liegen, bzw. gif2oledbatch im gleichen Ordner wie der Bilderordner.

#### Einzelbild
`python gif2oled.py mein-bild.png --out out_ordner`

#### Mehrere Bilder in einem Ordner (.png, .jpg, .jpeg, .bmp, .webp)
`python gif2oled.py Bilder_oled --out out_ordner`

#### Animation aus Einzelbildern
`python gif2oled.py Bilder_oled --out out_ordner`

#### Animation aus Gif oder MP4
`python gif2oled.py animation.gif  --out out_ordner --fps 8`


out_ordner ist der Ordner, in dem der Output gespeichert wird.

Die .bin Dateien auf dem ESP speichern. In Thonny (View > Files > Rechtsklick auf Dateien > Upload to)
