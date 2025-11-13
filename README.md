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
<p align="center">
  <img src="https://github.com/user-attachments/assets/b203ed56-afe1-408d-9b7b-04b8b87241ba" width="300">
  <img src="https://github.com/user-attachments/assets/49e5d98a-321c-4182-bb1a-e0fe96744230" width="300">
  <img src="https://github.com/user-attachments/assets/84c20ed1-a9b6-4cc7-98f0-d054b6d16974" width="300">
  <img src="https://github.com/user-attachments/assets/a7d39fa1-1b0f-4321-9d60-4a3f192e605d" width="300">
</p>

