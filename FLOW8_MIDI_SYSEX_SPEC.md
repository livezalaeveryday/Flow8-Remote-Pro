# Behringer FLOW 8 - USB MIDI & SysEx Protocol Specification 🎛️⚡
> **Authoritative Reverse-Engineered Architecture Specification**  
> Firmware Base: v11748 (ARM Cortex-R / ARMv7-R Architecture)  
> Analysis Target: `FLOW8_app.bin` (SHA-256: `325329885f962456b56ce351929f107904583c7d63916bc16fcbc1f0de674c2b`)

---

## 1. Overview & Hardware Interfaces

The Behringer FLOW 8 digital mixer natively supports bidirectional control over USB Class-Compliant MIDI. 

There are two primary control paradigms:
1. **Real-time Channel Voice Control (MIDI CC & Program Change)**: Zero-latency faders, mutes, solos, preamp gain, low-cut, pans, phantom power, and GEQ.
2. **Full State Transfer (MIDI SysEx Dump & Inject)**: 2,600-byte DSP snapshots containing complete parametric EQ (PEQ), compressors, routing, delays, and FX engines.

---

## 2. Bus Architecture & MIDI Channel Allocation

Found in firmware routine `0x01a3e0` – `0x01a590` and lookup tables at `0x0585dc` / `0x0585e7`:

| MIDI Channel | Hex Status | Target Section | Internal Bus ID | Functionality |
| :--- | :--- | :--- | :--- | :--- |
| **Channels 1–7** | `0xB0`–`0xB6` | **INPUT CH 1–7** | `0x00`–`0x06` | Channel Strip Controls, Sends (Main/Mon1/Mon2/FX1/FX2), 4-Band PEQ |
| **Channel 8** | `0xB7` | **MAIN BUS** | `0x0F` (15) | Main Stereo Master Fader, Mute, Balance, Limiter, 9-Band GEQ |
| **Channel 9** | `0xB8` | **MONITOR 1 BUS** | `0x0A` (10) | Monitor 1 Master Fader, Mute, Limiter, 9-Band GEQ |
| **Channel 10** | `0xB9` | **MONITOR 2 BUS** | `0x0B` (11) | Monitor 2 Master Fader, Mute, Limiter, 9-Band GEQ |
| **Channel 11** | `0xBA` | **FX 1 RETURN BUS** | `0x0C` (12) | FX 1 Master Return Level & Mute |
| **Channel 12** | `0xBB` | **FX 2 RETURN BUS** | `0x0D` (13) | FX 2 Master Return Level & Mute |
| **Channel 14** | `0xBD` / `0xCD` | **FX 1 ENGINE** | Engine 1 | FX 1 Preset Select (PC `0–15`), Decay/Speed (`CC 1`), Mode Switch (`CC 2`) |
| **Channel 15** | `0xBE` / `0xCE` | **FX 2 ENGINE** | Engine 2 | FX 2 Preset Select (PC `0–15`), Feedback/Filter (`CC 1`), Mode (`CC 2`), Tempo (`CC 3`) |
| **Channel 16** | `0xBF` / `0xCF` | **GLOBAL CONTROL** | System | Snapshot Recall (PC `0–15`), Global FX Mute & Tap Tempo |

> **Note on PHONES Output**:  
> The physical rotary knob on the top right of the FLOW 8 is an **analog potentiometer** directly feeding the headphone amplifier IC. It does not have a software volume fader. However, the monitoring source (Main vs Solo) is digitally switched via **CC 6 (Solo)**.

---

## 3. Real-Time Control Change (CC) Jump Table

### 3.1 Input Channels 1–7 (`MIDI Ch 1–7`)
Found in firmware routine `0x01a440` – `0x01a804` and send lookup table `0x0585dc` (`0F FF FF FF FF FF FF 0A 0B 0C 0D`):

| CC Number | Target Function | Value Range | Behavior & Resolution |
| :--- | :--- | :--- | :--- |
| **CC 1–4** | **4-Band PEQ Gain** | `0 - 127` | Bands 1–4 Gain: `-15 dB` (`0`) to `+15 dB` (`127`), `0 dB` = `64` |
| **CC 5** | **Channel Mute** | `0` or `127` | `0` = Unmuted (Audio Pass), `1..127` = Muted (Cut) |
| **CC 6** | **Channel Solo (PFL)** | `0` or `127` | `0` = Solo Off, `1..127` = Solo On (routes to Phones bus) |
| **CC 7** | **MAIN Send Fader** | `0 - 127` | `-∞ dB` (`0`), `-70 dB` (`1`) to `+10 dB` (`127`), `0 dB` ≈ `111` |
| **CC 8** | **Analog Preamp Gain** | `0 - 127` | Analog/digital gain control (`-20 dB` to `+60 dB`) |
| **CC 9** | **Low-Cut Filter (HPF)** | `0 - 127` | High-pass filter frequency: Off (`0`), `20 Hz` (`1`) to `600 Hz` (`127`) |
| **CC 10** | **Pan / Balance** | `0 - 127` | Stereo position: `0` (Hard Left), `64` (Center), `127` (Hard Right) |
| **CC 11** | **Compressor** | `0 - 100` | 1-Knob Compressor intensity (`0%` = Off to `100%` = Max) |
| **CC 12** | **+48V Phantom Power** | `0` or `127` | Physical relay trigger (Ch 1–2): `0` = Off, `1..127` = +48V Active |
| **CC 14** | **MON 1 Send Fader** | `0 - 127` | Channel Send Level to Monitor 1 (`-∞` to `+10 dB`) |
| **CC 15** | **MON 2 Send Fader** | `0 - 127` | Channel Send Level to Monitor 2 (`-∞` to `+10 dB`) |
| **CC 16** | **FX 1 Send Fader** | `0 - 127` | Channel Send Level to FX 1 Reverb (`-∞` to `+10 dB`) |
| **CC 17** | **FX 2 Send Fader** | `0 - 127` | Channel Send Level to FX 2 Delay (`-∞` to `+10 dB`) |
| **CC 21–24**| **4-Band PEQ Frequency** | `0 - 127` | Bands 1–4 Frequency: `20 Hz` (`0`) to `20 kHz` (`127`) logarithmic |
| **CC 31–34**| **4-Band PEQ Q Factor** | `0 - 127` | Bands 1–4 Q Width: `0.1` (`0`) to `10.0` (`127`) |

### 3.2 Master Buses (`MIDI Ch 8–12`: MAIN, MON 1, MON 2, FX 1, FX 2)
Found in firmware routine `0x01a4b8` – `0x01a538` and `0x01a8c8` – `0x01a9e4`:

| CC Number | Target Function | Value Range | Behavior & Resolution |
| :--- | :--- | :--- | :--- |
| **CC 5** | **Bus Mute** | `0` or `127` | `0` = Unmuted, `1..127` = Muted |
| **CC 7** | **Master Bus Fader** | `0 - 127` | Master output level (`-∞` to `+10 dB`) |
| **CC 8** | **Bus Limiter** | `0 - 127` | Output Limiter Threshold (`-24 dB` to `0 dB`) |
| **CC 10** | **Bus Balance** | `0 - 127` | Stereo Bus Balance (`0` = L, `64` = Center, `127` = R) |
| **CC 11–19**| **9-Band GEQ Gain** | `0 - 127` | Bands 1–9 Gain (`-15 dB` to `+15 dB`, `64` = `0 dB`) |
| **CC 21–29**| **9-Band GEQ Freq** | `0 - 127` | Bands 1–9 Parametric Frequency (`20 Hz` to `20 kHz`) |
| **CC 31–39**| **9-Band GEQ Q Factor** | `0 - 127` | Bands 1–9 Parametric Q Width (`0.1` to `10.0`) |

### Program Change (`0xCn`) - Instant Snapshot Recall
* **Status Byte**: `0xC0`
* **Data Byte**: `0 - 15` (Snapshot 1 through Snapshot 16)
* Triggers instantaneous internal DSP preset load in routine `0x01a3f4`.

---

## 4. MIDI System Exclusive (SysEx) Protocol

FLOW 8 uses SysEx for complete mixer state exchange (the same engine utilized by the OLED menu `MIDI-DUMP`).

### 4.1 SysEx Header Frame
```text
F0 00 20 32 21 00 [Unpacked 7-bit Data...] F7
```
* `F0` : SysEx Start
* `00 20 32` : MMA Manufacturer ID (Behringer / Music Tribe)
* `21` : Model ID (`0x21` = 33 decimal = FLOW 8)
* `00` : Target Device / Broadcast ID
* `F7` : End of Exclusive (EOX)

### 4.2 Payload Un-nibblizing (7-bit to 8-bit)
Because MIDI data bytes cannot exceed `0x7F`, 8-bit firmware words are un-nibblized using the routine at address `0x01adc8` (`AND 0x7F` + `LSL #6`).

### 4.3 2,600-Byte DSP Snapshot Format
When un-nibblized, the binary payload matches the DSP work buffer structure (`0x200deb70`):

| Offset | Length | Description |
| :--- | :--- | :--- |
| `0x4d0` | 4 bytes | Magic Identifier: `"FLOW"` (`0x574f4c46`) |
| `0x4d4` | 4 bytes | Protocol Revision Flag |
| `0x4d8` | 4 bytes | **CRC-32 Checksum** (Calculated over the 2,600 DSP bytes with seed `0xFFFFFFFF`) |
| `0x4e0` | **2,600 bytes** | **DSP Parameter Block** (`0x0a28` bytes) |

#### Contents of the 2,600-Byte DSP Block:
* **Channels 1–8 Parametric EQ (PEQ)**:
  - Band 1 (Low Shelf / Bell): Frequency, Gain, Q
  - Band 2 (Parametric Mid 1): Frequency, Gain, Q
  - Band 3 (Parametric Mid 2): Frequency, Gain, Q
  - Band 4 (High Shelf / Bell): Frequency, Gain, Q
* **Channels 1–8 Compressor**:
  - Threshold (-60 dB to 0 dB)
  - Ratio (1:1 to 50:1)
  - Attack Time (0.1 ms to 100 ms)
  - Release Time (50 ms to 3000 ms)
* **Master Section**:
  - `0x414`: MON 1 Master Output Level
  - `0x415`: MON 2 Master Output Level
  - `0x416`: Output Delay (Mon 1/2) (0 to 300 ms)
  - `0x417`: Analog Sensitivity Switch (+4 dBu / -10 dBV)
  - `0x424`: FX 1 Master Return Level
  - `0x425`: FX 2 Master Return Level
* **FX1 Engine (Reverb)**: Ambience, Room, Concert, Church, Cathedral, Stadium, Plate parameters.
* **FX2 Engine (Delay/Modulation)**: Delay times, Tap tempo, Feedback, Modulation speed, Tremolo.

---

## 5. Firmware Decryption Specification

* **Target File**: `BEHRINGER_FLOW8_v11748.bin`
* **Algorithm**: `AES-256-CBC`
* **Key Derivation**: `EVP_BytesToKey` (MD5 with 8-byte salt at offset `8..16`)
* **Secret Password Generation (`pgen`)**:
  ```python
  def pgen(SourceName):
      ch = "6stuv#*'~abcdnLMNziABCDopqrST()=?`'+23;:_,.-<>|45ijklPQR7890^?!?$%&/'mXYZ1wxyGHIJUVWefghKEFO"
      pw = ''
      otherName = 'SimplyPut'
      for i in range(1, 8):
          cc1 = ord(SourceName[-i]) - 48
          cc2 = ord(otherName[i]) - 48
          pw += ch[abs(cc1)] + ch[abs(cc2)]
      return pw
  # pgen('BEHRINGER_FLOW8_v11748')
  ```
* **Decompression**: Payload is compressed with standard `gzip`.
