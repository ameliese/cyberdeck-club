from machine import Pin, disable_irq, enable_irq
import time

# Zustandstabelle fuer Quadratur-Dekodierung: Index = (alter Zustand << 2) | neuer Zustand
_TABLE = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)


class Encoder:
  """Drehgeber (Rotary Encoder) mit CLK- und DT-Pin, per Interrupt ausgelesen.

  clk, dt            GPIO-Nummern von CLK und DT
  invert             True, um die Drehrichtung umzukehren
  steps_per_detent   Signalwechsel pro Rastung (meist 4, manche Module 2 oder 1)
  """

  def __init__(self, clk, dt, invert=False, steps_per_detent=4, sw=None):
    self.clk = Pin(clk, Pin.IN, Pin.PULL_UP)
    self.dt = Pin(dt, Pin.IN, Pin.PULL_UP)
    self.sign = -1 if invert else 1
    self.steps = steps_per_detent
    self.sw = Pin(sw, Pin.IN, Pin.PULL_UP) if sw is not None else None
    self.was_pressed = False
    self.press_t = 0
    self.turned = False
    self.state = (self.clk.value() << 1) | self.dt.value()
    self.acc = 0
    both = Pin.IRQ_FALLING | Pin.IRQ_RISING
    self.clk.irq(trigger=both, handler=self._irq)
    self.dt.irq(trigger=both, handler=self._irq)

  def _irq(self, pin):
     new = (self.clk.value() << 1) | self.dt.value()
     self.acc += _TABLE[(self.state << 2) | new] * self.sign
     self.state = new

  def read(self):
    """Gibt die Rastungen seit dem letzten Aufruf zurueck (+ = rechts, - = links)."""
    irq = disable_irq()
    n = int(self.acc / self.steps)
    self.acc -= n * self.steps
    enable_irq(irq)
    if n and self.pressed():
      self.turned = True      # gedreht, waehrend der Knopf gedrueckt war
    return n
    
  def pressed(self):
    return self.sw is not None and self.sw.value() == 0

  def clicked(self, max_ms=500):
    now = self.pressed()
    hit = False
    if now and not self.was_pressed:        # Knopf wurde gerade gedrueckt
        self.press_t = time.ticks_ms()
        self.turned = False
    elif self.was_pressed and not now:      # Knopf wurde gerade losgelassen
        hit = (not self.turned
               and time.ticks_diff(time.ticks_ms(), self.press_t) < max_ms)
    self.was_pressed = now
    return hit
    
