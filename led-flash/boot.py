# boot.py
import network, time
try:
    from config import WIFI_SSID, WIFI_PASS, HOSTNAME
except:
    WIFI_SSID = WIFI_PASS = None
    HOSTNAME = "esp"

sta = network.WLAN(network.STA_IF)
ap  = network.WLAN(network.AP_IF)

def connect_wifi(ssid, pwd, timeout_ms=15000):
    sta.active(True)
    try:
        sta.config(dhcp_hostname=HOSTNAME)
    except:
        pass
    sta.connect(ssid, pwd)
    t0 = time.ticks_ms()
    while not sta.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
        time.sleep_ms(200)
    return sta.isconnected()

if WIFI_SSID and WIFI_PASS and connect_wifi(WIFI_SSID, WIFI_PASS):
    ap.active(False)
    print("WiFi connected:", sta.ifconfig())  # -> ('ip','mask','gw','dns')
else:
    # fallback AP so you can still reach it at 192.168.4.1
    ap.active(True)
    ap.config(essid="DryerSetup", password="")
    sta.active(False)
    print("Started AP 'DryerSetup' — browse http://192.168.4.1")

