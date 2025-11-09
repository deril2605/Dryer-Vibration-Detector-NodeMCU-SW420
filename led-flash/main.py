# main.py  — minimal HTTP server for ESP8266 (MicroPython)
import usocket as socket
from machine import Pin
import network

# On NodeMCU the onboard LED is usually GPIO2 (D4) and is ACTIVE-LOW
LED_ACTIVE_LOW = True
LED_PIN_NUM = 2  # try 2 first; if your LED doesn't respond, try 16
led = Pin(LED_PIN_NUM, Pin.OUT, value=1 if LED_ACTIVE_LOW else 0)

def led_on():
    led.value(0 if LED_ACTIVE_LOW else 1)

def led_off():
    led.value(1 if LED_ACTIVE_LOW else 0)

# Build the little web page
HTML = """<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ESP Web</title>
<style>
body{font-family:-apple-system,system-ui,Segoe UI,Roboto,Helvetica,Arial;margin:24px}
.card{max-width:420px;margin:auto;padding:18px;border:1px solid #ddd;border-radius:12px}
.btn{display:inline-block;padding:10px 14px;margin:6px;border:1px solid #999;border-radius:10px;text-decoration:none;color:#111}
.on{background:#e9fbe9} .off{background:#fde9e9}
</style></head><body>
<div class="card">
  <h2>ESP8266 Web Server</h2>
  <p>Tap a button to toggle the onboard LED.</p>
  <p>
    <a class="btn on"  href="/on">Turn ON</a>
    <a class="btn off" href="/off">Turn OFF</a>
  </p>
  <p><a class="btn" href="/status">Status JSON</a></p>
</div>
</body></html>"""

def http_response(body, ctype="text/html; charset=utf-8"):
    hdr = "HTTP/1.1 200 OK\r\nContent-Type: {}\r\nCache-Control: no-store\r\n\r\n".format(ctype)
    return (hdr + body).encode() if isinstance(body, str) else hdr.encode() + body

def serve(port=80):
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(2)
    print("HTTP listening on port", port)

    while True:
        cl, remote = s.accept()
        try:
            req = cl.recv(512)
            path = b"/"
            if req:
                try:
                    path = req.split(b" ")[1]
                except:
                    pass

            if path == b"/" or path.startswith(b"/index"):
                resp = http_response(HTML)
            elif path == b"/on":
                led_on()
                resp = http_response(HTML)
            elif path == b"/off":
                led_off()
                resp = http_response(HTML)
            elif path == b"/status":
                import ujson, time
                ip = network.WLAN(network.STA_IF).ifconfig()[0] if network.WLAN(network.STA_IF).isconnected() else "192.168.4.1"
                body = ujson.dumps({"led": "on" if (led.value()==0 if LED_ACTIVE_LOW else led.value()==1) else "off",
                                    "ip": ip})
                resp = http_response(body, "application/json")
            else:
                resp = b"HTTP/1.1 404 Not Found\r\n\r\n"

            cl.sendall(resp)
        except Exception as e:
            try:
                cl.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
            except:
                pass
        finally:
            cl.close()

# Start the server
serve()

