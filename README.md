# 🧺 ESP Dryer Monitor (MicroPython)

Monitor your dryer using an **ESP32/ESP8266** + **SW-420 vibration sensor** and a clean local web dashboard — no cloud required.

This project lights an LED when the dryer is running and hosts a mobile-friendly web page showing real-time status.

> ✅ iPhone-friendly UI  
> ✅ Local-only, no cloud  
> ✅ Interrupt-based vibration detection  
> ✅ Auto-refresh status page  
> ✅ Active-low LED support  

---

## 📸 Demo

The dashboard shows:

- Dryer **RUNNING / IDLE**
- **Run time** in seconds / minutes
- LED status indicator
- Auto-refresh tag (5s)

---

## 🧰 Hardware Required

| Component | Notes |
|---|---|
| ESP32 / ESP8266 | MicroPython compatible |
| SW-420 vibration sensor | Detects dryer drum movement |
| 10k resistor (recommended) | Pull-down for clean signal |
| USB power cable | Power your ESP |
| Dryer 🫠 | The noisy kind |

---

## 📡 How It Works

1. SW-420 detects vibration  
2. ESP handles interrupts + debounce  
3. Times last vibration hit  
4. If silent for X seconds = dryer is idle  
5. Serves a pretty web UI over LAN

---

## 🛠 Wiring

| SW-420 Pin | ESP Pin |
|---|---|
| VCC | 3.3V |
| GND | GND |
| OUT | GPIO14 *(default, configurable)* |

> Turn the sensor’s trim-pot to adjust sensitivity.

---

Upload `main.py` to your board via **Thonny**, **ampy**, or `mpremote`.

---

