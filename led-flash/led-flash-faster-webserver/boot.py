# boot.py — Wi-Fi connect + quiet boot (works on ESP8266/ESP32)

import network, gc

# (Optional) silence ROM debug on some ports
try:
    import esp
    esp.osdebug(None)
except Exception:
    pass

SSID = "XYZ WIFI - 2.4Ghz"
PASSWORD = "XYZ"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# (Optional ESP32) reduce latency by disabling Wi-Fi power save
try:
    wlan.config(pm=0)
except Exception:
    pass

if not wlan.isconnected():
    wlan.connect(SSID, PASSWORD)
    # simple wait
    import time
    for _ in range(60):  # ~6s
        if wlan.isconnected():
            break
        time.sleep(0.1)

print("WiFi:", "connected" if wlan.isconnected() else "not connected")
if wlan.isconnected():
    print("ifconfig:", wlan.ifconfig())

gc.collect()

