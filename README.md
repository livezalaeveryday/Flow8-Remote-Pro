# FLOW 8 Pro Studio Remote (Offline & LAN Edition) 🎛️⚡

คอนโซลควบคุมดิจิทัลมิกเซอร์ **Behringer FLOW 8** (Firmware v11748) ระดับมืออาชีพผ่าน USB Web MIDI และระบบเครือข่าย LAN พร้อมสถาปัตยกรรม **Multi-Screen Real-Time Sync** และ **Single MIDI Master**

---

## 🌟 ฟีเจอร์เด่น (Key Features)

### 1. Bidirectional Hardware Sync (MIDI IN & MIDI OUT)
- ซิงค์ 2 ทิศทางระหว่างหน้าจอและตัวฮาร์ดแวร์จริง
- ขยับก้านเฟดเดอร์หรือหมุนลูกบิดบนตัวเครื่อง หน้าจอจะขยับตามทันที
- เลื่อนเฟดเดอร์บนหน้าจอ คอนโซลจะส่ง MIDI CC ไปยังเครื่องทันที

### 2. Multi-Screen Real-Time Sync & LAN Remote
- รองรับการเปิดควบคุมพร้อมกันหลายหน้าจอ ทั้งคอมพิวเตอร์หลัก, iPad, แท็บเล็ต Android และสมาร์ตโฟน
- **ขยับ Fader หน้าจอไหน จออื่นทุกจอก็ขยับตามทันทีแบบ Real-Time** ด้วยระบบ **Server-Sent Events (SSE)**
- **Hardware State as Single Source of Truth**: รีเฟรชหน้าจอกี่ครั้ง ค่าปัจจุบันก็ไม่หาย ดึงข้อมูลกลับมาแสดงผลทันที

### 3. Localhost MIDI Master Architecture
- หน้าจอเครื่องคอมพิวเตอร์หลัก (`http://localhost:8844`) เป็นตัวเชื่อมต่อ Web MIDI API เพียงตัวเดียว ป้องกันปัญหา MIDI Driver ถูกแย่งใช้ (Single Master)
- อุปกรณ์ผ่านแลน (`http://192.168.x.x:8844`) จะส่ง Action ไปยังเซิร์ฟเวอร์ และเซิร์ฟเวอร์จะบรอดแคสต์ให้ Localhost ส่งออกคำสั่ง MIDI สู่มิกเซอร์

### 4. 🎛️ New Studio FX Dual Rack (Reverb & Delay/Modulation)
- สกัดและจัดระเบียบ 32 อัลกอริทึมตรงจาก Firmware `v11748`:
  - **FX 1 (16 Reverbs)**: `AMBIENCE`, `PERC-REV1`, `PERC-REV2`, `GUIT-REV1`, `GUIT-REV2`, `CHAMBER`, `ROOM`, `CONCERT`, `CHURCH`, `CATHEDRAL`, `TEMPLE`, `STADIUM`, `FLANGER`, `SOFT CHORUS`, `WARM CHORUS`, `DEEP CHORUS`
  - **FX 2 (16 Delays & Modulations)**: `DELAY 1/1..2/1`, `ECHO 1/1..2/1`, `WIDE ECHO`, `PING PONG`, `PING P 1/3`, `PING P R>L`
- **Spatial Pan Balance พร้อมปุ่มลัดแยกเสียงออกซ้าย**:
  - `[◀ L ONLY]`: แพนเสียงเอฟเฟกต์ 100% ออกเฉพาะลำโพง MAIN ซ้าย
  - `[⬤ STEREO]`: มิติสเตอริโอ Center กลาง
  - `[R ONLY ▶]`: แพนเสียงเอฟเฟกต์ 100% ออกเฉพาะลำโพง MAIN ขวา
- **Tone Switch Filter ประจำแต่ละอัลกอริทึม**: `VOCAL` (คัทเบสย่านต่ำ) vs `INSTRUMENT`, `DULL` (ลดแหลมคม) vs `BRIGHT`, `LESS BASS` vs `MORE BASS`
- **Tap Tempo Studio Center**: รองรับการเคาะจังหวะด้วยปุ่มหรือกด **Spacebar** บนคีย์บอร์ด คำนวณเป็น BPM และ Milliseconds ให้ทันที

### 5. Steinberg StudioEQ & 9-Band Master Graphic EQ
- **Channels 1–7**: 4-Band Parametric EQ สไตล์ Steinberg Cubase StudioEQ พร้อม Real-time RTA Spectrum Analyzer
- **Master & Monitor Buses**: 9-Band Graphic Equalizer (GEQ) แยกอิสระสำหรับ Main L/R, MON 1 และ MON 2

### 6. Direct Numeric Typing & Step Buttons
- พิมพ์ตัวเลขค่า dB, Hz, % ได้โดยตรงในทุกช่อง
- ปุ่มลูกศร Step (▲ / ▼) สำหรับขยับละเอียดทีละ 0.1 dB หรือ 0.5 dB
- ดับเบิ้ลคลิกพร้อมกด Ctrl ที่ก้านเฟดเดอร์หรือลูกบิด เพื่อรีเซ็ตค่าเป็น Unity (0.0 dB / 12 o'clock) ทันที

### 7. ⚠️ Master Reset Dialog
- ปุ่มรีเซ็ตใหญ่ที่แถบด้านบน คืนค่ามิกเซอร์กลับสู่มาตรฐานได้อย่างรวดเร็ว:
  - **🔴 Factory Reset All**: คืนค่าโรงงานทุกส่วน
  - **🎚 Reset All Faders**: คืนค่าก้านเฟดเดอร์ทุกช่องเป็น 0.0 dB
  - **〰 Reset All EQs to Flat**: รีเซ็ต EQ และ Compressor ทุกช่องเป็นทางราบ

---

## 🚀 วิธีเปิดใช้งาน (Getting Started)

### ขั้นตอนที่ 1: เตรียมฮาร์ดแวร์
1. เสียบสาย **USB** จาก Behringer FLOW 8 เข้าคอมพิวเตอร์ Windows
2. เปิดสวิตช์เปิดเครื่องมิกเซอร์

### ขั้นตอนที่ 2: เริ่มการทำงาน
1. ดับเบิ้ลคลิกที่ไฟล์ **`start_remote.bat`**
2. คอนโซลจะเปิดเบราว์เซอร์ (Google Chrome / Microsoft Edge) ขึ้นมาอัตโนมัติที่:
   ```
   http://localhost:8844
   ```
3. ไฟสถานะสีเขียวที่แถบด้านบนจะแสดง `FLOW 8 MIDI` พร้อมใช้งานทันที

### ขั้นตอนที่ 3: ใช้งานผ่าน iPad / แท็บเล็ต / มือถือในวง LAN เดียวกัน
1. นำอุปกรณ์เชื่อมต่อ Wi-Fi วงเดียวกับคอมพิวเตอร์
2. เปิดเบราว์เซอร์บน iPad/มือถือ แล้วเข้า URL ที่แสดงบนหน้าจอคอมพิวเตอร์ เช่น:
   ```
   http://192.168.1.110:8844
   ```
3. กดย่อ-ขยายหน้าจอให้พอดี และสามารถเลื่อนเฟดเดอร์ควบคุมได้พร้อมกันทันที

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
flow8-pro-remote/
├── index.html            # Single-Page App (Offline PC & LAN Console UI)
├── server.py             # Python HTTP + Server-Sent Events (SSE) Sync Engine
├── start_remote.bat      # Windows One-Click Launcher
├── default_library.json  # Firmware Library Snapshot Reference
├── live_session.json     # Current Mixer Session State (Auto-saved)
├── .gitignore
└── README.md
```

---

## 📄 License
MIT License
