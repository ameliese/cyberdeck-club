# Access Point mit Website, erreichbar über WLAN und IP Adresse
# Zeichnen mit Maus oder Touch (Java Script, derived from Drawing Lines: Revised by Darren Kessner. Edited and maintained by p5.js Contributors and Processing Foundation. Licensed under CC BY-NC-SA 4.0. https://creativecommons.org/licenses/by-nc-sa/4.0/
# https://p5js.org/examples/Animation-And-Variables-Drawing-Lines/)
# CC BY-NC-SA 4.0. https://creativecommons.org/licenses/by-nc-sa/4.0/

try:
  import usocket as socket
except:
  import socket

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'MicroPython-AP' # WLAN Name
password = '12345678' # Passwort mit mind. 8 Zeichen

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK) # mit passwort


while ap.active() == False:
  pass

print('Connection successful')
print(ap.ifconfig())

def web_page():
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">

<style>body{margin:0;background:#000}canvas{display:block;touch-action:none}
h1{position:fixed;top:10px;left:10px;margin:0;font-family:sans-serif;color:#fff;pointer-events:none}</style></head>
<body><h1>Draw</h1><canvas id="c"></canvas><script>

var c=document.getElementById('c'),x=c.getContext('2d'),px=0,py=0,d=false;
c.width=innerWidth;c.height=innerHeight;
x.lineWidth=10;x.lineCap='round';
c.onpointerdown=function(e){d=true;px=e.clientX;py=e.clientY};
c.onpointerup=function(){d=false};
c.onpointermove=function(e){
  if(!d)return;
  x.strokeStyle='hsl('+(e.clientX-e.clientY)+',82%,50%)';
  x.beginPath();x.moveTo(px,py);x.lineTo(e.clientX,e.clientY);x.stroke();
  px=e.clientX;py=e.clientY;
};
</script></body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  print('Content = %s' % str(request))
  response = web_page()
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()
  

