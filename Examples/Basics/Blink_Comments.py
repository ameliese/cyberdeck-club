from machine import Pin # hier binden wir Pin aus dem Modul machine ein
from time import sleep # hier binden wir sleep, also eine Pause (in Sekunden) aus dem Modul time ein
led = Pin(2, Pin.OUT) # funktioniert, weil wir vorher Pin importiert haben
while True: # Schleife, die nie endet. Alles, was eingerückt hier drunter steht, läuft immer wieder von vorn. Bis sie gestoppt wird, z.B. mit strg/cmd+C
  led.value(not led.value()) # Der aktuelle Zustand der LED wird bei jedem Durchlauf ausgelesen. Ist er 1 (an) wird er zu 0 (aus) und andersrum.
  sleep(0.5) # Halbe Sekunde Pause, damit man das Blinken auch sieht
  
  # ginge auch so:
  #led.on()
  #sleep(0.5)
  #led.off()
  #sleep(0.5)
  
  # oder so
  #led.value(1)
  #sleep(0.5)
  #led.value(0)
  #sleep(0.5)