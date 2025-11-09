# main.py — iPhone-friendly MicroPython HTTP server (line-by-line header read)

import socket
from machine import Pin

# On-board LED (GPIO2 on many ESP8266/ESP32 boards; change if needed)
led = Pin(2, Pin.OUT)

def web_page():
    state = "OFF" if led.value() == 1 else "ON"
    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>ESP Web Server</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
    html{font-family:Helvetica,Arial,sans-serif;display:inline-block;margin:0 auto;text-align:center}
    h1{color:#0F3376;padding:2vh}
    p{font-size:1.2rem}
    .button{display:inline-block;background:#e7bd3b;border:none;border-radius:4px;color:#fff;padding:14px 32px;text-decoration:none;font-size:24px;margin:4px;cursor:pointer}
    .button2{background:#4286f4}
  </style>
</head>
<body>
  <h1>ESP Web Server</h1>
  <p>GPIO state: <strong>""" + state + """</strong></p>
  <p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>
</body>
</html>"""

def _sendall(sock, data):
    # MicroPython's send() can be partial; loop until all bytes are written
    if isinstance(data, str):
        data = data.encode("utf-8")
    mv = memoryview(data)
    total = 0
    n = len(mv)
    while total < n:
        sent = sock.send(mv[total:])
        if sent is None:
            continue
        total += sent

def serve(port=80):
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
    s.bind(addr)
    s.listen(2)
    print("HTTP listening on :{}".format(port))

    while True:
        cl, remote = s.accept()
        try:
            cl.settimeout(3)
            # --- Read request headers line-by-line (Arduino-style) ---
            cl_file = cl.makefile("rwb", 0)
            request_line = None
            while True:
                line = cl_file.readline()
                if not line:
                    break
                if request_line is None:
                    request_line = line  # e.g. b"GET /path?x=1 HTTP/1.1\r\n"
                # end of headers is a blank line
                if line == b"\r\n":
                    break

            if not request_line:
                cl.close()
                continue

            # --- Parse method & path (minimal) ---
            try:
                parts = request_line.decode("utf-8", "ignore").strip().split()
                method = parts[0]
                path = parts[1] if len(parts) > 1 else "/"
            except Exception:
                method, path = "GET", "/"

            # iOS Safari often requests /favicon.ico; respond quickly
            if path.startswith("/favicon.ico"):
                _sendall(cl, "HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n")
                cl.close()
                continue

            # LED actions via query string
            if "/?led=on" in path:
                led.value(0)
            elif "/?led=off" in path:
                led.value(1)

            body = web_page().encode("utf-8")
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                "Content-Length: {length}\r\n"
                "Connection: close\r\n"
                "Cache-Control: no-cache\r\n"
                "\r\n"
            ).format(length=len(body)).encode("utf-8")

            try:
                cl.settimeout(10)  # give time to flush to Safari
            except Exception:
                pass

            _sendall(cl, headers)
            _sendall(cl, body)

        except Exception as e:
            try:
                _sendall(
                    cl,
                    "HTTP/1.1 500 Internal Server Error\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Connection: close\r\n\r\n"
                    "Internal error: {}\n".format(e),
                )
            except Exception:
                pass
        finally:
            try:
                cl.close()
            except Exception:
                pass

if __name__ == "__main__":
    serve(80)

