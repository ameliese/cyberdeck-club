# Licensed under CC BY-NC-SA 4.0. https://creativecommons.org/licenses/by-nc-sa/4.0/
#(Java Script Code derived from Kaleidoscope: Revised by Kasey Lichtlyter. Edited and maintained by p5.js Contributors and Processing Foundation. Licensed under CC BY-NC-SA 4.0., https://creativecommons.org/licenses/by-nc-sa/4.0/
# https://p5js.org/examples/Repetition-Kaleidoscope/)


# ESP32 Access Point mit Website, erreichbar über WLAN und IP Adresse
# Zeichnen mit Maus oder Touch im Browser und simultan auf SSD1306 OLED Display 128x64px
# 2 Symmetrieachsen, Anzahl der Achsen in def_webpage() anpassen
# 2 Varianten für def_webpage() (Auflösung im Browser, die nicht gebrauchte jeweils auskommentieren)

try:
  import usocket as socket
except:
  import socket

import network
import esp
esp.osdebug(None)
import gc
gc.collect()
from machine import Pin, I2C
import ssd1306

# Display
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.show()

# Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='MicroPython-AP', password='12345678', authmode=network.AUTH_WPA_WPA2_PSK)
while not ap.active():
  pass
print(ap.ifconfig())

# Auflösung im Browser entspricht SSD1306 128x64px OLED
# def web_page():
#   return """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
# <style>body{margin:0;background:#000}canvas{display:block;width:100vw;image-rendering:pixelated;touch-action:none}
# button{position:fixed;top:10px;right:10px;font-family:sans-serif;padding:8px 14px}</style></head>
# <body><button id="b">Clear</button><canvas id="c" width="128" height="64"></canvas><script>
# var c=document.getElementById('c'),x=c.getContext('2d');
# var symmetry=2,angle=Math.PI*2/symmetry;
# var W=c.width,H=c.height,down=false,px=0,py=0,q=[];
# x.fillStyle='rgb(50,50,50)';x.fillRect(0,0,W,H);
# x.strokeStyle='#fff';x.lineWidth=1;
# 
# function pos(e){
#   var r=c.getBoundingClientRect();
#   return{x:(e.clientX-r.left)*W/r.width,y:(e.clientY-r.top)*H/r.height};
# }
# function seg(ax,ay,bx,by){x.beginPath();x.moveTo(ax,ay);x.lineTo(bx,by);x.stroke()}
# 
# c.onpointerdown=function(e){var p=pos(e);px=p.x;py=p.y;down=true};
# c.onpointerup=c.onpointerleave=function(){down=false};
# c.onpointermove=function(e){
#   if(!down)return;
#   var p=pos(e);
#   var sx=p.x-W/2,sy=p.y-H/2,ex=px-W/2,ey=py-H/2;
#   x.save();x.translate(W/2,H/2);
#   for(var i=0;i<symmetry;i++){
#     x.rotate(angle);
#     seg(sx,sy,ex,ey);
#     x.save();x.scale(1,-1);seg(sx,sy,ex,ey);x.restore();
#     var a=angle*(i+1),co=Math.cos(a),si=Math.sin(a);
#     for(var m=1;m>=-1;m-=2){
#       var u1=sx,v1=m*sy,u2=ex,v2=m*ey;
#       q.push([
#         Math.round(u1*co-v1*si+W/2),Math.round(u1*si+v1*co+H/2),
#         Math.round(u2*co-v2*si+W/2),Math.round(u2*si+v2*co+H/2)
#       ].join(','));
#     }
#   }
#   x.restore();
#   px=p.x;py=p.y;
# };
# 
# document.getElementById('b').onclick=function(){
#   q=[];
#   x.fillStyle='rgb(50,50,50)';x.fillRect(0,0,W,H);
#   fetch('/c').catch(function(){});
# };
# 
# setInterval(function(){
#   if(!q.length)return;
#   fetch('/l?'+q.splice(0,40).join(';')).catch(function(){});
# },60);
# </script></body></html>"""

# Höhere Auflösung im Browser mit Skalierungsfaktor S
def web_page(): 
  return """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{margin:0;background:#000;height:100vh;display:flex;align-items:center;justify-content:center}
canvas{display:block;width:min(100vw,200vh);aspect-ratio:2/1;touch-action:none}
button{position:fixed;top:10px;right:10px;font-family:sans-serif;padding:8px 14px}</style></head>
<body><button id="b">Clear</button><canvas id="c" width="512" height="256"></canvas><script>
var c=document.getElementById('c'),x=c.getContext('2d');
var S=4,symmetry=1,angle=Math.PI*2/symmetry;
var W=c.width,H=c.height,down=false,px=0,py=0,q=[];
x.fillStyle='rgb(50,50,50)';x.fillRect(0,0,W,H);
x.strokeStyle='#fff';x.lineWidth=S;x.lineCap='round';

function pos(e){
  var r=c.getBoundingClientRect();
  return{x:(e.clientX-r.left)*W/r.width,y:(e.clientY-r.top)*H/r.height};
}
function seg(ax,ay,bx,by){x.beginPath();x.moveTo(ax,ay);x.lineTo(bx,by);x.stroke()}

c.onpointerdown=function(e){var p=pos(e);px=p.x;py=p.y;down=true};
c.onpointerup=c.onpointerleave=function(){down=false};
c.onpointermove=function(e){
  if(!down)return;
  var p=pos(e);
  var sx=p.x-W/2,sy=p.y-H/2,ex=px-W/2,ey=py-H/2;
  x.save();x.translate(W/2,H/2);
  for(var i=0;i<symmetry;i++){
    x.rotate(angle);
    seg(sx,sy,ex,ey);
    x.save();x.scale(1,-1);seg(sx,sy,ex,ey);x.restore();
    var a=angle*(i+1),co=Math.cos(a),si=Math.sin(a);
    for(var m=1;m>=-1;m-=2){
      var u1=sx,v1=m*sy,u2=ex,v2=m*ey;
      q.push([
        Math.round((u1*co-v1*si+W/2)/S),Math.round((u1*si+v1*co+H/2)/S),
        Math.round((u2*co-v2*si+W/2)/S),Math.round((u2*si+v2*co+H/2)/S)
      ].join(','));
    }
  }
  x.restore();
  px=p.x;py=p.y;
};

document.getElementById('b').onclick=function(){
  q=[];
  x.fillStyle='rgb(50,50,50)';x.fillRect(0,0,W,H);
  fetch('/c').catch(function(){});
};

setInterval(function(){
  if(!q.length)return;
  fetch('/l?'+q.splice(0,40).join(';')).catch(function(){});
},60);
</script></body></html>"""

def draw(data):
  for s in data.split(';'):
    try:
      a, b, c2, d = [int(v) for v in s.split(',')]
      oled.line(a, b, c2, d, 1)
    except:
      pass
  oled.show()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  conn.settimeout(2)
  try:
    req = conn.recv(2048).decode()
    parts = req.split('\r\n')[0].split(' ')
    path = parts[1] if len(parts) > 1 else '/'
    ctype = 'text/plain'
    status = '200 OK'
    if path.startswith('/l?'):
      draw(path[3:])
      body = 'ok'
    elif path == '/c':
      oled.fill(0)
      oled.show()
      body = 'cleared'
    elif path == '/':
      ctype = 'text/html'
      body = web_page()
    else:
      status = '404 Not Found'
      body = 'nope'
    conn.send('HTTP/1.1 ' + status + '\r\n')
    conn.send('Content-Type: ' + ctype + '\r\n')
    conn.send('Connection: close\r\n\r\n')
    conn.sendall(body)
  except Exception as e:
    print('err', e)
  conn.close()