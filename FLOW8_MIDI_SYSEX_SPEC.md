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

## 2. Bus Architecture & MIDI Channel Routing

FLOW 8 partitions its 6 internal mixing buses by **MIDI Channel (`0xBn`)**:

| MIDI Channel | Hex Status | Bus Name | Functionality |
| :--- | :--- | :--- | :--- |
| **Channel 1** | `0xB0` | **MAIN L/R** | Main Stereo Mix (Faders, Mutes, Solos, Pans, Main GEQ) |
| **Channel 2** | `0xB1` | **MONITOR 1** | Monitor 1 Aux Send Faders & Mon 1 GEQ |
| **Channel 3** | `0xB2` | **MONITOR 2** | Monitor 2 Aux Send Faders & Mon 2 GEQ |
| **Channel 4** | `0xB3` | **FX 1 (Reverb)** | FX 1 Reverb Send Levels |
| **Channel 5** | `0xB4` | **FX 2 (Delay)** | FX 2 Delay / Modulation Send Levels |
| **Channel 6** | `0xB5` | **PHONES / SOLO** | Headphone Solo Bus Monitoring (PFL / AFL switch) |

> **Note on PHONES Output**:  
> The physical rotary knob on the top right of the FLOW 8 is an **analog potentiometer** directly feeding the headphone amplifier IC. It does not have a software volume fader. However, the monitoring source (Main vs Solo) is digitally switched via **CC 6 (Solo)**.

---

## 3. Real-Time Control Change (CC) Jump Table

Found in firmware routine `0x01a440` – `0x01a680`:

| CC Number | Target Function | Value Range | Behavior & Resolution |
| :--- | :--- | :--- | :--- |
| **CC 5** | **Channel Mute** | `0` or `127` | `0` = Unmuted (Audio Pass), `127` = Muted (Cut) |
| **CC 6** | **Channel Solo** | `0` or `127` | `0` = Solo Off, `127` = Solo On (routes to Phones bus) |
| **CC 7** | **Channel Fader** | `0 - 127` | Logarithmic taper: -∞ dB (`0`) to +10 dB (`127`), 0 dB ~ `96` |
| **CC 8** | **Analog Preamp Gain** | `0 - 127` | Ch 1 & 2 analog gain control (-20 dB to +60 dB) |
| **CC 9** | **Low-Cut Filter** | `0 - 127` | High-pass filter frequency: 20 Hz (`0`) to 600 Hz (`127`) |
| **CC 10** | **Pan / Balance** | `0 - 127` | Stereo position: `0` (Hard Left), `64` (Center), `127` (Hard Right) |
| **CC 11** | **+48V Phantom Power** | `0` or `127` | Physical relay trigger: `0` = Off, `127` = +48V Active |
| **CC 12–19**| **9-Band Graphic EQ** | `0 - 127` | Main/Mon GEQ bands: 63Hz, 125Hz, 250Hz, 500Hz, 1k, 2k, 4k, 8k, 16k (-15dB to +15dB) |

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
