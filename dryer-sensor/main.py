# main.py — SW-420 dryer sensor + auto LED indicator + simple webpage
# Works on ESP8266/ESP32 + iPhone friendly

import socket
from machine import Pin
import time

# ----------------- CONFIG -----------------
LED_PIN = 2                 # On-board LED (active-LOW)
SENSOR_PIN = 14             # SW-420 digital output pin (ex: D5 on ESP8266)
RUN_TIMEOUT_MS = 10000      # 20s without vibration = idle
SENSOR_ACTIVE_HIGH = True   # SW-420 outputs HIGH when vibration
# ------------------------------------------

led = Pin(LED_PIN, Pin.OUT)
sensor = Pin(SENSOR_PIN, Pin.IN)

# Ensure LED OFF at start
led.value(1)  # active-LOW

_last_hit_ms = -10_000_000
_last_irq_ms = -10_000_000
_DEBOUNCE_MS = 50

_running = False
_run_started_ms = None

def _now():
    return time.ticks_ms()

def _mark_hit():
    global _last_hit_ms
    _last_hit_ms = _now()

def _irq(pin):
    global _last_irq_ms
    now = _now()
    if time.ticks_diff(now, _last_irq_ms) < _DEBOUNCE_MS:
        return
    _last_irq_ms = now
    v = pin.value()
    if (v == 1 and SENSOR_ACTIVE_HIGH) or (v == 0 and not SENSOR_ACTIVE_HIGH):
        _mark_hit()

# attach interrupt
try:
    sensor.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=_irq)
except Exception:
    pass

def dryer_running():
    # poll in case IRQ missed
    v = sensor.value()
    if (v == 1 and SENSOR_ACTIVE_HIGH) or (v == 0 and not SENSOR_ACTIVE_HIGH):
        _mark_hit()

    now = _now()
    running_now = time.ticks_diff(now, _last_hit_ms) < RUN_TIMEOUT_MS

    # track transitions to record when the run started
    global _running, _run_started_ms
    if running_now and not _running:
        _run_started_ms = now               # just transitioned to running
    elif not running_now and _running:
        _run_started_ms = None              # back to idle

    _running = running_now
    return running_now


def update_led():
    if dryer_running():
        led.value(0)   # ON (active low)
    else:
        led.value(1)   # OFF

def web_page():
    running = dryer_running()
    status = "RUNNING" if running else "IDLE"
    # use the run-start timestamp for duration (not _last_hit_ms)
    if running and _run_started_ms is not None:
        secs = time.ticks_diff(_now(), _run_started_ms) // 1000
        if secs < 60:
            time_text = f"running for {secs}s"
        else:
            mins = secs // 60
            time_text = f"running for {mins} min"
    else:
        time_text = ""
    # Colors for the badge
    badge_bg = "#16a34a" if running else "#dc2626"   # green / red
    badge_txt = "#ffffff"
    note = "Detecting vibration from the dryer drum." if running else "No vibration detected recently."

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dryer Monitor</title>
<meta http-equiv="refresh" content="5">
<style>
  :root {{
    --card-max: 520px;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 24px;
    font-family: -apple-system, system-ui, Segoe UI, Roboto, Arial, sans-serif;
    background: #f6f7fb;
    color: #111827;
    display: grid; place-items: center; min-height: 100vh;
  }}
  .card {{
    width: 100%; max-width: var(--card-max);
    background: #fff; border: 1px solid #e5e7eb; border-radius: 16px;
    padding: 20px 20px 24px; box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    text-align: center;
  }}
  h1 {{ margin: 6px 0 8px; font-size: 22px; }}
  .sub {{ margin: 0 0 16px; color: #6b7280; font-size: 14px; }}
  .badge {{
    display:inline-block; padding: 10px 18px; border-radius: 999px;
    font-weight: 700; letter-spacing: .4px; margin: 8px 0 16px;
    background: {badge_bg}; color: {badge_txt};
  }}
  .row {{
    display:flex; justify-content:center; gap:12px; flex-wrap:wrap;
    margin-top: 8px; font-size: 14px; color:#374151;
  }}
  .pill {{
    border:1px solid #e5e7eb; border-radius:999px; padding:6px 12px; background:#fafafa;
  }}
  .foot {{ margin-top:16px; color:#9ca3af; font-size:12px; }}
</style>
</head>
<body>
  <div class="card">
    <h1>Dryer Monitor</h1>
    <p class="sub">{note}</p>
    <div class="badge">{status}</div>
    <div class="sub">{time_text}</div>
    <div class="row">
      <div class="pill">Auto-refresh: 5s</div>
      <div class="pill">Sensor: SW-420</div>
      <div class="pill">LED: {'ON' if running else 'OFF'}</div>
    </div>
    <div class="foot">ESP web server • MicroPython</div>
  </div>
</body>
</html>"""


def _sendall(sock, data):
    if isinstance(data, str):
        data = data.encode()
    mv = memoryview(data)
    while mv:
        sent = sock.send(mv)
        mv = mv[sent:]

def serve(port=80):
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    try: s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except: pass
    s.bind(addr); s.listen(2)
    print("HTTP listening on :80")

    while True:
        update_led()
        cl, addr = s.accept()
        try:
            cl.settimeout(3)
            f = cl.makefile("rwb", 0)
            req = None
            while True:
                line = f.readline()
                if not line: break
                if req is None:
                    req = line
                if line == b"\r\n": break

            # Skip favicon
            if req and b"favicon" in req:
                _sendall(cl, "HTTP/1.1 204 No Content\r\n\r\n")
                cl.close()
                continue

            body = web_page().encode()
            hdr = f"HTTP/1.1 200 OK\r\nContent-Length: {len(body)}\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n".encode()
            cl.settimeout(5)
            _sendall(cl, hdr); _sendall(cl, body)

        except:
            pass
        finally:
            try: cl.close()
            except: pass

if __name__ == "__main__":
    serve()


