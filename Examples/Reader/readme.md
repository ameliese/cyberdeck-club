## Reader
1	Deinen Text als .txt (UTF-8) speichern und per Thonny ins Hauptverzeichnis des ESP32 hochladen.
2	"dein-text.txt" umbenennen
3 Findet er keine text.txt, zeigt er eine Hinweismeldung.

### `reader.py` + `reader-own-font.py`
• Taster an GPIO 4 scrollt zurück, GPIO 5 scrollt weiter.

•	Ein Druck scrollt eine Zeile. Gedrückt halten startet nach 0,3 s das Dauer-Scrollen.

•	Rechts zeigt ein schmaler Balken die Position im Text.

•	[mehr Infos zu custom Fonts](https://github.com/ameliese/cyberdeck-club/tree/main/Examples/Own_Font)

### `reader_encoder.py`, `reader-own-font-encoder-import-encoder.py`+ `reader_encoder_menu.py`
• nutzen das Modul `encoder` (aus dem Ordner [Modules](https://github.com/ameliese/cyberdeck-club/tree/main/Examples/Modules) runterladen und auf ESP im lib Ordner oder im Hauptverzeichnis speichern)
