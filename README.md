# FLOW 8 Pro Studio Remote — Windows Desktop & Multi-Screen LAN Console 🎛️⚡

[![Latest Release](https://img.shields.io/github/v/release/livezalaeveryday/Flow8-Remote-Pro?color=00d2ff&label=Latest%20Release&style=for-the-badge)](https://github.com/livezalaeveryday/Flow8-Remote-Pro/releases/latest)
[![Total Downloads](https://img.shields.io/github/downloads/livezalaeveryday/Flow8-Remote-Pro/total?color=22c55e&label=EXE%20Downloads&style=for-the-badge)](https://github.com/livezalaeveryday/Flow8-Remote-Pro/releases)
[![License: Free Non-Commercial](https://img.shields.io/badge/License-Free%20Non--Commercial-f59e0b?style=for-the-badge)](./LICENSE)
[![Platform: Windows 10/11](https://img.shields.io/badge/Platform-Windows%2010%2F11%20%2B%20LAN-3b82f6?style=for-the-badge)](https://github.com/livezalaeveryday/Flow8-Remote-Pro/releases)

A standalone **Windows Desktop Mixing Console (`.exe`)** and **Multi-Screen Wi-Fi/LAN Remote Hub** for the **Behringer FLOW 8** digital mixer (Firmware `v11748` / `v11749`).

Built on a native Windows Multimedia (`winmm.dll`) USB MIDI engine and a real-time Server-Sent Events (SSE) synchronization hub, **FLOW 8 Pro Studio Remote** delivers zero-latency hardware control on Windows PCs while allowing simultaneous wireless control from iPads, Android tablets, and smartphones over local Wi-Fi.

---

## 📥 Download Standalone Windows App (`.exe`)

👉 **[Download `FLOW8_Remote_Pro.exe` from GitHub Releases](https://github.com/livezalaeveryday/Flow8-Remote-Pro/releases/latest)**

* **Single-File Portable Executable (`~8.8 MB`)** — No Python installation or external MIDI drivers required.
* **Plug & Play USB MIDI** — Automatically detects and connects to `FLOW 8 MIDI OUT` and `FLOW 8 MIDI IN` directly through the Windows OS kernel.

---

## 🌟 Key Features

### 1. Native Windows USB MIDI Engine (`winmm.dll`)
* **Direct Hardware Binding**: Connects directly to the FLOW 8 USB MIDI interface at the Windows OS level—no browser Web MIDI permission prompts required.
* **Auto-Reconnect Watchdog**: Automatically detects and reconnects within 3 seconds if the USB cable is unplugged or the mixer is power-cycled.
* **Bidirectional Sync (`MIDI IN` & `MIDI OUT`)**: Moving physical faders on the FLOW 8 updates all connected screens in real time; moving controls on any screen immediately drives the hardware DSP.

### 2. Full Hardware Bus & DSP Control (Firmware v11748 Verified)
* **7 Input Channels (`CH 1–7`)**:
  * Independent Bus Send Faders for **MAIN**, **MON 1**, **MON 2**, **FX 1**, and **FX 2** (`CC 7`, `CC 14–17`).
  * Analog Preamp Gain (`-20 dB` to `+60 dB`), `+48V` Phantom Power (CH 1–2), Low-Cut HPF (`20 Hz` to `600 Hz`), Phase Invert, 1-Knob Compressor (`CC 11`), Stereo Pan (`CC 10`), Solo PFL (`CC 6`), and Mute (`CC 5`).
* **5 Master Output Buses (`MAIN`, `MON 1`, `MON 2`, `FX 1`, `FX 2` on `MIDI Ch 8–12`)**:
  * Master Fader Level (`CC 7`), Bus Mute (`CC 5`), Stereo Balance (`CC 10`), Output Limiter (`-24 dB` to `0 dB`, `CC 8`), and Speaker Alignment Delay (`0.0 ms` to `341.0 ms` with automatic meter/feet calculation).

### 3. Interactive 4-Band StudioEQ & 9-Band Parametric Master GEQ
* **Channels 1–7 (4-Band StudioEQ)**: Drag-and-drop 2D parametric nodes (`20 Hz – 20 kHz`, `-15 dB to +15 dB`), mouse-wheel Q control (`0.1 – 10.0`), musical note/cent readout, real-time RTA spectrum visualizer, and multi-genre instrument presets.
* **Master & Monitor Buses (9-Band Parametric GEQ)**: Interactive 9-node EQ curve + graphic sliders for **MAIN**, **MON 1**, and **MON 2** (`CC 11–19` Gain, `CC 21–29` Freq, `CC 31–39` Q) with live PA, broadcast, and music mastering presets.

### 4. Dual 32-Bit Studio FX Rack (32 Hardware Algorithms)
* **FX 1 (16 Reverb & Space Engines)**: `AMBIENCE`, `PERC-REV 1/2`, `GUIT-REV 1/2`, `CHAMBER`, `ROOM`, `CONCERT`, `CHURCH`, `CATHEDRAL`, `TEMPLE`, `STADIUM`, `FLANGER`, `SOFT/WARM/DEEP CHORUS`.
* **FX 2 (16 Delay, Echo & Modulation Engines)**: `DELAY 1/1..2/1`, `ECHO 1/1..2/1`, `WIDE ECHO`, `PING PONG`, `PING P 1/3`, `PING P R>L`, and Chorus/Flanger.
* **Quick Stereo Spatial Panning**: Instant `[◀ L ONLY]`, `[⬤ STEREO]`, and `[R ONLY ▶]` routing buttons plus Tap Tempo (`[SPACEBAR]` hotkey or click) with BPM and millisecond readouts.

### 5. Multi-Screen Wi-Fi / LAN Remote Hub
* While `FLOW8_Remote_Pro.exe` runs on your Windows PC connected via USB, any **iPad, Android tablet, or phone** on the same Wi-Fi network can open `http://<YOUR-PC-LAN-IP>:8844` to mix wirelessly in full synchronization.

### 6. Mobile App Library (`New_8.json`) Import & Export
* Export your complete session (channel labels, gains, HPF, 4-band PEQ, and 9-band Master/Monitor GEQ) to `New_8.json` for direct import into the official Behringer FLOW Mix mobile app.

---

## 🚀 Getting Started

### Option A: Standalone Windows Executable (Recommended)
1. Connect your **Behringer FLOW 8** to your Windows PC via USB and power it on.
2. Double-click **`FLOW8_Remote_Pro.exe`**.
3. The dedicated desktop console window will open automatically and connect to `FLOW 8 MIDI OUT (USB DIRECT)`.
4. *(Optional)* Click the **`🌐 LAN`** badge in the top bar to copy your local Wi-Fi URL for iPads, tablets, or smartphones.

### Option B: Run from Python Source
```bash
# Launch standalone desktop window + background native MIDI hub
python flow8_desktop.py

# Or run as a headless HTTP + Native MIDI server only
python server.py
```

---

## 📁 Repository Structure

```text
Flow8-Remote-Pro/
├── FLOW8_Remote_Pro.exe          # Standalone Windows Desktop Application (Single-File EXE)
├── flow8_desktop.py              # Windows Desktop App Window & Server Lifecycle Launcher
├── server.py                     # Native WinMM USB MIDI Engine + Real-Time SSE HTTP Server
├── index.html                    # Studio Mixing Console UI (4-Band PEQ, 9-Band GEQ, Dual FX Rack)
├── start_remote.bat              # One-Click Windows Batch Launcher
├── flow8.ico                     # Application Icon
├── default_library.json          # Reference FLOW 8 Library Structure for New_8.json Export
├── live_session.json             # Auto-saved Real-Time Mixer Session State
├── FLOW8_MIDI_SYSEX_SPEC.md      # Reverse-Engineered Behringer FLOW 8 MIDI & SysEx Specification
├── scripts/
│   ├── decrypt_flow8_firmware.py # Firmware AES-256-CBC Decryption & Extraction Utility
│   ├── flow8_sysex_parser.py     # 2,600-Byte DSP SysEx Snapshot Encoder/Decoder
│   └── check_usage_stats.py      # Utility to check GitHub Release EXE download & repo stats
└── LICENSE                       # Free Non-Commercial License Agreement
```

---

## 📜 License — Free for Non-Commercial Use Only

This software and its compiled executable (`FLOW8_Remote_Pro.exe`) are released **FREE OF CHARGE** strictly for **personal, educational, research, and non-commercial use**.

> **🚫 Commercial Use Prohibited:**  
> Selling, reselling, renting, bundling with commercial products, or charging fees for this software or derivative works is strictly prohibited. See the [LICENSE](./LICENSE) file for full terms.
