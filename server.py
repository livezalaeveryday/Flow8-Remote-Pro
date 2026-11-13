import http.server
import socket
import os
import sys
import json
import time
import math
import threading
import queue
import ctypes

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

PORT = 8844

# Support both normal Python script and PyInstaller frozen .exe
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
    BUNDLE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_DIR

SESSION_FILE = os.path.join(APP_DIR, "live_session.json")

# -----------------------------------------------------------------------------
# DEFAULT INITIAL MIXER SESSION STATE
# -----------------------------------------------------------------------------
GEQ_BASE_FREQS = [63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

def create_default_session():
    channels = [
        {"id": 0, "name": "DYN-MIC", "gain": 40.0, "lowcut": 80.0, "hpfOn": False, "comp": 0.0, "pan": 64, "mute": False, "solo": False, "phantom": False, "busSends": {"main": 100, "mon1": 77, "mon2": 77, "fx1": 64, "fx2": 64}, "peqFreq": [100, 2000, 5000, 11290], "peqQ": [1.0, 0.8, 0.8, 1.0], "peqGain": [0.0, 0.0, 0.0, 0.0], "peqType": ["lowshelf", "peak", "peak", "hishelf"], "peqBypass": [False, False, False, False]},
        {"id": 1, "name": "C-MIC", "gain": 40.0, "lowcut": 80.0, "hpfOn": False, "comp": 0.0, "pan": 64, "mute": False, "solo": False, "phantom": True, "busSends": {"main": 100, "mon1": 77, "mon2": 77, "fx1": 64, "fx2": 64}, "peqFreq": [100, 1000, 2610, 11290], "peqQ": [1.0, 0.8, 0.8, 1.0], "peqGain": [0.0, 0.0, 0.0, 0.0], "peqType": ["lowshelf", "peak", "peak", "hishelf"], "peqBypass": [False, False, False, False]},
        {"id": 2, "name": "COMBO 3", "gain": 0.0, "lowcut": 80.0, "hpfOn": False, "comp": 0.0, "pan": 64, "mute": False, "solo": False, "phantom": False, "busSends": {"main": 100, "mon1": 77, "mon2": 77, "fx1": 64, "fx2": 64}, "peqFreq": [100, 1000, 2610, 11290], "peqQ": [1.0, 0.8, 0.8, 1.0], "peqGain": [0.0, 0.0, 0.0, 0.0], "peqType": ["lowshelf", "peak", "peak", "hishelf"], "peqBypass": [False, False, False, False]},
        {"id": 3, "name": "COMBO 4", "gain": 0.0, "lowcut": 80.0, "hpfOn": False, "comp": 0.0, "pan": 64, "mute": False, "solo": False, "phantom": False, "busSends": {"main": 100, "mon1": 77, "mon2": 77, "fx1": 64, "fx2": 64}, "peqFreq": [100, 1000, 2610, 11290], "peqQ": [1.0, 0.8, 0.8, 1.0], "peqGain": [0.0, 0.0, 0.0, 0.0], "peqType": ["lowshelf", "peak", "peak", "hishelf"], "peqBypass": [False, False, False, False]},
        {"id": 4, "name": "LINE 5/6", "gain": 0.0, "lowcut": 80.0, "hpfOn": False, "comp": 0.0, "pan": 64, "mute": False, "solo": False, "phantom": False, "busSends": {"main": 100, "mon1": 77, "mon2": 77, "fx1": 64, "fx2": 64}, "peqFreq": [100, 1000, 2610, 11290], "peqQ": [1.0, 0.8, 0.8, 1.0], "peqGain": [0.0, 0.0, 0.0, 0.0], "peqType": ["lowshelf", "peak", "peak", "hishelf"], "peqBypass": [False, False, False, False]},
        {"id": 5, "name": "LINE 7/8", "gain": 0.0, "lowcut": 80.0, "hpfOn": False, "comp": 0.0, "pan": 64, "mute": False, "solo": False, "phantom": False, "busSends": {"main": 100, "mon1": 77, "mon2": 77, "fx1": 64, "fx2": 64}, "peqFreq": [100, 1000, 2610, 11290], "peqQ": [1.0, 0.8, 0.8, 1.0], "peqGain": [0.0, 0.0, 0.0, 0.0], "peqType": ["lowshelf", "peak", "peak", "hishelf"], "peqBypass": [False, False, False, False]},
        {"id": 6, "name": "USB / BT", "gain": 0.0, "lowcut": 80.0, "hpfOn": False, "comp": 0.0, "pan": 64, "mute": False, "solo": False, "phantom": False, "busSends": {"main": 100, "mon1": 77, "mon2": 77, "fx1": 64, "fx2": 64}, "peqFreq": [100, 1000, 2610, 11290], "peqQ": [1.0, 0.8, 0.8, 1.0], "peqGain": [0.0, 0.0, 0.0, 0.0], "peqType": ["lowshelf", "peak", "peak", "hishelf"], "peqBypass": [False, False, False, False]}
    ]
    master_buses = {
        "main": {"level": 100, "limiterdB": 0.0, "pandB": 0.0, "delay": 0.0, "mute": False, "geqFreq": list(GEQ_BASE_FREQS), "geqGain": [0.0]*9, "geqQ": [1.0]*9},
        "mon1": {"level": 77, "limiterdB": 0.0, "pandB": 0.0, "delay": 0.0, "mute": False, "geqFreq": list(GEQ_BASE_FREQS), "geqGain": [0.0]*9, "geqQ": [1.0]*9},
        "mon2": {"level": 77, "limiterdB": 0.0, "pandB": 0.0, "delay": 0.0, "mute": False, "geqFreq": list(GEQ_BASE_FREQS), "geqGain": [0.0]*9, "geqQ": [1.0]*9},
        "fx1": {"level": 100, "mute": False},
        "fx2": {"level": 100, "mute": False}
    }
    fx_state = {
        "fx1": {"presetIdx": 0, "param1": 50, "param2Idx": 0, "pan": 64, "levelMain": 100, "levelMon1": 77, "levelMon2": 77, "mute": False},
        "fx2": {"presetIdx": 0, "param1": 50, "param2Idx": 0, "tempoMs": 500, "bpm": 120.0, "pan": 64, "levelMain": 100, "levelMon1": 77, "levelMon2": 77, "mute": False}
    }
    return {
        "version": 1,
        "currentBus": "main",
        "channels": channels,
        "masterBuses": master_buses,
        "fxState": fx_state
    }

session_lock = threading.Lock()
if os.path.exists(SESSION_FILE):
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            live_session = json.load(f)
    except Exception as e:
        print(f"Error loading session, resetting: {e}")
        live_session = create_default_session()
else:
    live_session = create_default_session()

def save_session():
    with session_lock:
        try:
            with open(SESSION_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(live_session, f, indent=2)
            os.replace(SESSION_FILE + ".tmp", SESSION_FILE)
        except Exception as e:
            print(f"Failed to save session: {e}")

# -----------------------------------------------------------------------------
# REAL-TIME SSE (SERVER-SENT EVENTS) BROADCASTER
# -----------------------------------------------------------------------------
sse_subscribers = []
sse_lock = threading.Lock()

def broadcast_sse(event_dict, exclude_clientId=None):
    payload = f"data: {json.dumps(event_dict)}\n\n".encode("utf-8")
    dead_clients = []
    with sse_lock:
        for q, client_id in sse_subscribers:
            if exclude_clientId and client_id == exclude_clientId:
                continue
            try:
                q.put_nowait(payload)
            except Exception:
                dead_clients.append((q, client_id))
        for item in dead_clients:
            if item in sse_subscribers:
                sse_subscribers.remove(item)

# -----------------------------------------------------------------------------
# NATIVE WINDOWS WINMM.DLL USB MIDI ENGINE (ZERO EXTERNAL DEPENDENCIES)
# -----------------------------------------------------------------------------
MIM_DATA = 0x3C3
CALLBACK_FUNCTION = 0x00030000

class MIDIOUTCAPSW(ctypes.Structure):
    _fields_ = [
        ("wMid", ctypes.c_uint16),
        ("wPid", ctypes.c_uint16),
        ("vDriverVersion", ctypes.c_uint32),
        ("szPname", ctypes.c_wchar * 32),
        ("wTechnology", ctypes.c_uint16),
        ("wVoices", ctypes.c_uint16),
        ("wNotes", ctypes.c_uint16),
        ("wChannelMask", ctypes.c_uint16),
        ("dwSupport", ctypes.c_uint32),
    ]

class MIDIINCAPSW(ctypes.Structure):
    _fields_ = [
        ("wMid", ctypes.c_uint16),
        ("wPid", ctypes.c_uint16),
        ("vDriverVersion", ctypes.c_uint32),
        ("szPname", ctypes.c_wchar * 32),
        ("dwSupport", ctypes.c_uint32),
    ]

MIDIINPROC = ctypes.WINFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.c_size_t,
)

class NativeFlow8MidiEngine:
    def __init__(self):
        self.winmm = ctypes.windll.winmm if sys.platform == "win32" else None
        self.lock = threading.Lock()
        self.h_out = ctypes.c_void_p(0)
        self.h_in = ctypes.c_void_p(0)
        self.out_name = ""
        self.in_name = ""
        self.connected = False
        self._cb_ref = MIDIINPROC(self._midi_in_callback) if self.winmm else None

    def _midi_in_callback(self, h_midi_in, w_msg, dw_instance, dw_param1, dw_param2):
        if w_msg != MIM_DATA:
            return
        status_byte = dw_param1 & 0xFF
        data1 = (dw_param1 >> 8) & 0x7F
        data2 = (dw_param1 >> 16) & 0x7F
        status_hi = status_byte & 0xF0
        ch = status_byte & 0x0F

        if status_hi == 0xB0:
            self._handle_incoming_cc(ch, data1, data2)

    def _handle_incoming_cc(self, ch, cc, val):
        # Hardware FLOW 8 knob/fader moved -> update live_session & broadcast SSE
        evt = None
        with session_lock:
            if 0 <= ch < 7:
                c = live_session["channels"][ch]
                if cc == 7:
                    c["busSends"]["main"] = val
                    evt = {"action": "setFader", "channel": ch, "bus": "main", "value": val, "source": "hardware"}
                elif cc == 14:
                    c["busSends"]["mon1"] = val
                    evt = {"action": "setFader", "channel": ch, "bus": "mon1", "value": val, "source": "hardware"}
                elif cc == 15:
                    c["busSends"]["mon2"] = val
                    evt = {"action": "setFader", "channel": ch, "bus": "mon2", "value": val, "source": "hardware"}
                elif cc == 16:
                    c["busSends"]["fx1"] = val
                    evt = {"action": "setFader", "channel": ch, "bus": "fx1", "value": val, "source": "hardware"}
                elif cc == 17:
                    c["busSends"]["fx2"] = val
                    evt = {"action": "setFader", "channel": ch, "bus": "fx2", "value": val, "source": "hardware"}
                elif cc == 5:
                    m = val >= 64
                    c["mute"] = m
                    evt = {"action": "setMute", "channel": ch, "value": m, "source": "hardware"}
                elif cc == 6:
                    s = val >= 64
                    c["solo"] = s
                    evt = {"action": "setSolo", "channel": ch, "value": s, "source": "hardware"}
                elif cc == 10:
                    c["pan"] = val
                    evt = {"action": "setPan", "channel": ch, "value": val, "source": "hardware"}
            elif 7 <= ch <= 11:
                bus_names = {7: "main", 8: "mon1", 9: "mon2", 10: "fx1", 11: "fx2"}
                bus = bus_names.get(ch, "main")
                if bus in live_session["masterBuses"]:
                    if cc == 7:
                        live_session["masterBuses"][bus]["level"] = val
                        evt = {"action": "setMasterFader", "bus": bus, "value": val, "source": "hardware"}
                    elif cc == 5:
                        m = val >= 64
                        live_session["masterBuses"][bus]["mute"] = m
                        evt = {"action": "setMasterMute", "bus": bus, "value": m, "source": "hardware"}
        if evt:
            broadcast_sse(evt)

    def scan_and_connect(self):
        if not self.winmm:
            return False
        with self.lock:
            # Verify existing connection is still present in device list
            found_out_idx = -1
            found_out_name = ""
            num_out = self.winmm.midiOutGetNumDevs()
            for i in range(num_out):
                caps = MIDIOUTCAPSW()
                if self.winmm.midiOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
                    if "FLOW 8" in caps.szPname.upper() or "FLOW8" in caps.szPname.upper():
                        found_out_idx = i
                        found_out_name = caps.szPname
                        break

            if found_out_idx == -1:
                if self.connected:
                    self._close_locked()
                return False

            if self.connected and self.h_out.value:
                return True

            # Open MIDI OUT
            h_out = ctypes.c_void_p(0)
            res_out = self.winmm.midiOutOpen(ctypes.byref(h_out), found_out_idx, 0, 0, 0)
            if res_out == 0 and h_out.value:
                self.h_out = h_out
                self.out_name = found_out_name
                self.connected = True
                print(f"  [USB MIDI] Connected Output: {self.out_name} (dev {found_out_idx})")
            else:
                self.connected = False
                return False

            # Also try opening MIDI IN
            num_in = self.winmm.midiInGetNumDevs()
            for i in range(num_in):
                caps = MIDIINCAPSW()
                if self.winmm.midiInGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
                    if "FLOW 8" in caps.szPname.upper() or "FLOW8" in caps.szPname.upper():
                        h_in = ctypes.c_void_p(0)
                        res_in = self.winmm.midiInOpen(
                            ctypes.byref(h_in), i, self._cb_ref, 0, CALLBACK_FUNCTION
                        )
                        if res_in == 0 and h_in.value:
                            self.h_in = h_in
                            self.in_name = caps.szPname
                            self.winmm.midiInStart(self.h_in)
                            print(f"  [USB MIDI] Connected Input : {self.in_name} (dev {i})")
                        break
            return True

    def _close_locked(self):
        if self.winmm:
            if self.h_in.value:
                try:
                    self.winmm.midiInStop(self.h_in)
                    self.winmm.midiInClose(self.h_in)
                except Exception:
                    pass
                self.h_in = ctypes.c_void_p(0)
            if self.h_out.value:
                try:
                    self.winmm.midiOutClose(self.h_out)
                except Exception:
                    pass
                self.h_out = ctypes.c_void_p(0)
        self.connected = False
        self.out_name = ""
        self.in_name = ""

    def close(self):
        with self.lock:
            self._close_locked()

    def send_short(self, status, data1, data2=0):
        if not self.winmm:
            return False
        with self.lock:
            if not self.connected or not self.h_out.value:
                return False
            dw_msg = (status & 0xFF) | ((data1 & 0x7F) << 8) | ((data2 & 0x7F) << 16)
            res = self.winmm.midiOutShortMsg(self.h_out, dw_msg)
            if res != 0:
                self._close_locked()
                return False
            return True

    def send_cc(self, channel_1based, cc, value):
        ch = max(0, min(15, int(channel_1based) - 1))
        cc_val = max(0, min(127, int(round(cc))))
        v_val = max(0, min(127, int(round(value))))
        return self.send_short(0xB0 | ch, cc_val, v_val)

    def send_pc(self, channel_1based, program_0based):
        ch = max(0, min(15, int(channel_1based) - 1))
        prog = max(0, min(127, int(round(program_0based))))
        return self.send_short(0xC0 | ch, prog, 0)

midi_engine = NativeFlow8MidiEngine()

def db_to_eq_raw(db_val):
    clamped = max(-15.0, min(15.0, float(db_val)))
    return int(round(((clamped + 15.0) / 30.0) * 127.0))

def freq_to_midi_raw(freq):
    f = max(20.0, min(20000.0, float(freq)))
    norm = (math.log10(f) - math.log10(20.0)) / (math.log10(20000.0) - math.log10(20.0))
    return max(0, min(127, int(round(norm * 127.0))))

def q_to_midi_raw(q):
    q_clamped = max(0.1, min(10.0, float(q)))
    norm = (q_clamped - 0.1) / 9.9
    return max(0, min(127, int(round(norm * 127.0))))

BUS_SEND_CC_MAP = {"main": 7, "mon1": 14, "mon2": 15, "fx1": 16, "fx2": 17}
MASTER_BUS_CH_MAP = {"main": 8, "mon1": 9, "mon2": 10, "fx1": 11, "fx2": 12}

def apply_action_to_hardware_midi(msg):
    """Translates UI/LAN action into exact Behringer FLOW 8 v11748 MIDI CCs."""
    if not midi_engine.connected:
        return
    action = msg.get("action")
    if action == "setFader":
        ch = int(msg.get("channel", 0)) + 1
        bus = msg.get("bus", "main")
        val = int(msg.get("value", 100))
        cc = BUS_SEND_CC_MAP.get(bus, 7)
        midi_engine.send_cc(ch, cc, val)

    elif action == "setMasterFader":
        bus = msg.get("bus", "main")
        val = int(msg.get("value", 100))
        bus_ch = MASTER_BUS_CH_MAP.get(bus, 8)
        midi_engine.send_cc(bus_ch, 7, val)

    elif action == "setPan":
        ch = int(msg.get("channel", 0)) + 1
        val = int(msg.get("value", 64))
        midi_engine.send_cc(ch, 10, val)

    elif action == "setMute":
        ch = int(msg.get("channel", 0)) + 1
        val = 127 if msg.get("value") else 0
        midi_engine.send_cc(ch, 5, val)

    elif action == "setMasterMute":
        bus = msg.get("bus", "main")
        bus_ch = MASTER_BUS_CH_MAP.get(bus, 8)
        val = 127 if msg.get("value") else 0
        midi_engine.send_cc(bus_ch, 5, val)

    elif action == "setSolo":
        ch = int(msg.get("channel", 0)) + 1
        val = 127 if msg.get("value") else 0
        midi_engine.send_cc(ch, 6, val)

    elif action == "setGain":
        ch = int(msg.get("channel", 0)) + 1
        gain_db = float(msg.get("value", 0.0))
        raw = int(round(((gain_db + 20.0) / 80.0) * 127.0))
        midi_engine.send_cc(ch, 8, raw)

    elif action == "setComp":
        ch = int(msg.get("channel", 0)) + 1
        comp_db = float(msg.get("value", 0.0))
        comp_pct = int(round((abs(comp_db) / 30.0) * 100.0))
        midi_engine.send_cc(ch, 11, comp_pct)

    elif action == "setHPF":
        ch = int(msg.get("channel", 0)) + 1
        on = bool(msg.get("value", False))
        cut = float(msg.get("lowcut", 80.0))
        if not on:
            midi_engine.send_cc(ch, 9, 0)
        else:
            raw = max(1, min(127, int(round(((cut - 20.0) / 580.0) * 127.0))))
            midi_engine.send_cc(ch, 9, raw)

    elif action == "set48V":
        ch = int(msg.get("channel", 0)) + 1
        val = 127 if msg.get("value") else 0
        midi_engine.send_cc(ch, 12, val)

    elif action == "setEqBand":
        ch = int(msg.get("channel", 0)) + 1
        b_idx = int(msg.get("bandIndex", 0))
        if "gain" in msg:
            midi_engine.send_cc(ch, 1 + b_idx, db_to_eq_raw(msg["gain"]))
        if "freq" in msg:
            midi_engine.send_cc(ch, 21 + b_idx, freq_to_midi_raw(msg["freq"]))
        if "q" in msg:
            midi_engine.send_cc(ch, 31 + b_idx, q_to_midi_raw(msg["q"]))

    elif action == "setGeqBand":
        bus = msg.get("bus", "main")
        bus_ch = MASTER_BUS_CH_MAP.get(bus, 8)
        b_idx = int(msg.get("bandIndex", 0))
        if "gain" in msg:
            midi_engine.send_cc(bus_ch, 11 + b_idx, db_to_eq_raw(msg["gain"]))
        if "freq" in msg:
            midi_engine.send_cc(bus_ch, 21 + b_idx, freq_to_midi_raw(msg["freq"]))
        if "q" in msg:
            midi_engine.send_cc(bus_ch, 31 + b_idx, q_to_midi_raw(msg["q"]))

    elif action == "setLimiter":
        bus = msg.get("bus", "main")
        bus_ch = MASTER_BUS_CH_MAP.get(bus, 8)
        lim_db = float(msg.get("value", 0.0))
        raw = int(round(((lim_db + 24.0) / 24.0) * 127.0))
        midi_engine.send_cc(bus_ch, 8, raw)

    elif action == "setBusBalance":
        bus = msg.get("bus", "main")
        bus_ch = MASTER_BUS_CH_MAP.get(bus, 8)
        bal = float(msg.get("value", 0.0))
        raw = int(round(((bal + 10.0) / 20.0) * 127.0))
        midi_engine.send_cc(bus_ch, 10, raw)

    elif action == "setFx":
        fx_num = int(msg.get("fxNum", 1))
        fx_engine_ch = 14 if fx_num == 1 else 15
        fx_bus_ch = 11 if fx_num == 1 else 12
        if "presetIdx" in msg:
            p_idx = int(msg["presetIdx"])
            midi_engine.send_pc(fx_engine_ch, p_idx)
        if "param1" in msg:
            midi_engine.send_cc(fx_engine_ch, 1, int(msg["param1"]))
        if "param2Idx" in msg:
            midi_engine.send_cc(fx_engine_ch, 2, 127 if int(msg["param2Idx"]) else 0)
        if "mute" in msg:
            midi_engine.send_cc(fx_bus_ch, 5, 127 if msg["mute"] else 0)
        if "levelMain" in msg:
            midi_engine.send_cc(fx_bus_ch, 7, int(msg["levelMain"]))

def midi_watchdog_loop():
    while True:
        try:
            midi_engine.scan_and_connect()
        except Exception:
            pass
        time.sleep(3.0)

# -----------------------------------------------------------------------------
# NETWORK UTILS
# -----------------------------------------------------------------------------
def get_all_ips():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
        if not lan_ip.startswith("127."):
            ips.append(lan_ip)
    except Exception:
        pass
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    return ips

# -----------------------------------------------------------------------------
# HTTP REQUEST HANDLER
# -----------------------------------------------------------------------------
class Flow8Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Prefer APP_DIR if index.html exists there, else BUNDLE_DIR
        serve_dir = APP_DIR if os.path.exists(os.path.join(APP_DIR, "index.html")) else BUNDLE_DIR
        super().__init__(*args, directory=serve_dir, **kwargs)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        # 0. API: Hardware & Network Status
        if self.path == "/api/status" or self.path.startswith("/api/status?"):
            ips = get_all_ips()
            primary_ip = ips[0] if ips else "127.0.0.1"
            status_obj = {
                "status": "ok",
                "midiConnected": midi_engine.connected,
                "midiOutName": midi_engine.out_name,
                "midiInName": midi_engine.in_name,
                "lanIps": ips,
                "lanUrl": f"http://{primary_ip}:{PORT}"
            }
            data = json.dumps(status_obj).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # 1. API: Get Live Session State (Used by clients on initial load and refresh)
        if self.path == "/api/session" or self.path.startswith("/api/session?"):
            with session_lock:
                data = json.dumps(live_session).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # 2. API: Server-Sent Events (Real-time Full Duplex push to all screens)
        if self.path.startswith("/api/events"):
            client_id = None
            if "clientId=" in self.path:
                client_id = self.path.split("clientId=")[1].split("&")[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            client_q = queue.Queue(maxsize=150)
            with sse_lock:
                sse_subscribers.append((client_q, client_id))

            init_msg = f"data: {json.dumps({'type': 'connected', 'clientId': client_id})}\n\n".encode("utf-8")
            try:
                self.wfile.write(init_msg)
                self.wfile.flush()
            except Exception:
                with sse_lock:
                    if (client_q, client_id) in sse_subscribers:
                        sse_subscribers.remove((client_q, client_id))
                return

            last_ping = time.time()
            try:
                while True:
                    try:
                        msg = client_q.get(timeout=1.0)
                        self.wfile.write(msg)
                        self.wfile.flush()
                    except queue.Empty:
                        pass

                    now = time.time()
                    if now - last_ping > 15.0:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
                        last_ping = now
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            finally:
                with sse_lock:
                    if (client_q, client_id) in sse_subscribers:
                        sse_subscribers.remove((client_q, client_id))
            return

        super().do_GET()

    def do_POST(self):
        if self.path == "/api/action":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            try:
                msg = json.loads(body.decode("utf-8"))
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {e}")
                return

            action = msg.get("action")
            client_id = msg.get("clientId")
            with session_lock:
                if action == "setFader":
                    ch = msg.get("channel", 0)
                    bus = msg.get("bus", "main")
                    val = msg.get("value", 100)
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["busSends"][bus] = val

                elif action == "setMasterFader":
                    bus = msg.get("bus", "main")
                    val = msg.get("value", 100)
                    if bus in live_session["masterBuses"]:
                        live_session["masterBuses"][bus]["level"] = val

                elif action == "setPan":
                    ch = msg.get("channel", 0)
                    val = msg.get("value", 64)
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["pan"] = val

                elif action == "setMute":
                    ch = msg.get("channel", 0)
                    val = bool(msg.get("value", False))
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["mute"] = val

                elif action == "setMasterMute":
                    bus = msg.get("bus", "main")
                    val = bool(msg.get("value", False))
                    if bus in live_session["masterBuses"]:
                        live_session["masterBuses"][bus]["mute"] = val

                elif action == "setSolo":
                    ch = msg.get("channel", 0)
                    val = bool(msg.get("value", False))
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["solo"] = val

                elif action == "setGain":
                    ch = msg.get("channel", 0)
                    val = float(msg.get("value", 0.0))
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["gain"] = val

                elif action == "setComp":
                    ch = msg.get("channel", 0)
                    val = float(msg.get("value", 0.0))
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["comp"] = val

                elif action == "setHPF":
                    ch = msg.get("channel", 0)
                    val = bool(msg.get("value", False))
                    cut = float(msg.get("lowcut", 80.0))
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["hpfOn"] = val
                        live_session["channels"][ch]["lowcut"] = cut

                elif action == "set48V":
                    ch = msg.get("channel", 0)
                    val = bool(msg.get("value", False))
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["phantom"] = val

                elif action == "setDelay":
                    bus = msg.get("bus", "main")
                    val = float(msg.get("value", 0.0))
                    if bus in live_session["masterBuses"]:
                        live_session["masterBuses"][bus]["delay"] = val

                elif action == "setLimiter":
                    bus = msg.get("bus", "main")
                    val = float(msg.get("value", 0.0))
                    if bus in live_session["masterBuses"]:
                        live_session["masterBuses"][bus]["limiterdB"] = val

                elif action == "setBusBalance":
                    bus = msg.get("bus", "main")
                    val = float(msg.get("value", 0.0))
                    if bus in live_session["masterBuses"]:
                        live_session["masterBuses"][bus]["pandB"] = val

                elif action == "setEqBand":
                    ch = msg.get("channel", 0)
                    bIdx = msg.get("bandIndex", 0)
                    if 0 <= ch < len(live_session["channels"]) and 0 <= bIdx < 4:
                        c_obj = live_session["channels"][ch]
                        if "gain" in msg:
                            c_obj["peqGain"][bIdx] = float(msg["gain"])
                        if "freq" in msg:
                            c_obj["peqFreq"][bIdx] = float(msg["freq"])
                        if "q" in msg:
                            c_obj["peqQ"][bIdx] = float(msg["q"])
                        if "peqType" in msg:
                            c_obj["peqType"][bIdx] = str(msg["peqType"])
                        if "bypass" in msg:
                            c_obj["peqBypass"][bIdx] = bool(msg["bypass"])

                elif action == "setGeqBand":
                    bus = msg.get("bus", "main")
                    bIdx = msg.get("bandIndex", 0)
                    if bus in live_session["masterBuses"] and 0 <= bIdx < 9:
                        m_obj = live_session["masterBuses"][bus]
                        if "gain" in msg and "geqGain" in m_obj:
                            m_obj["geqGain"][bIdx] = float(msg["gain"])
                        if "freq" in msg and "geqFreq" in m_obj:
                            m_obj["geqFreq"][bIdx] = float(msg["freq"])
                        if "q" in msg and "geqQ" in m_obj:
                            m_obj["geqQ"][bIdx] = float(msg["q"])

                elif action == "setFx":
                    fx_num = msg.get("fxNum", 1)
                    key = f"fx{fx_num}"
                    if "fxState" not in live_session:
                        live_session["fxState"] = {}
                    if key not in live_session["fxState"]:
                        live_session["fxState"][key] = {}
                    for prop in ["presetIdx", "param1", "param2Idx", "pan", "levelMain", "levelMon1", "levelMon2", "tempoMs", "bpm", "mute"]:
                        if prop in msg:
                            live_session["fxState"][key][prop] = msg[prop]

                elif action == "resetAll":
                    reset_type = msg.get("type", "factory")
                    if reset_type == "factory":
                        new_s = create_default_session()
                        live_session.clear()
                        live_session.update(new_s)
                    elif reset_type == "faders":
                        for c in live_session["channels"]:
                            for b in c["busSends"]:
                                c["busSends"][b] = 100
                        for b in live_session["masterBuses"]:
                            live_session["masterBuses"][b]["level"] = 100
                    elif reset_type == "eqs":
                        for c in live_session["channels"]:
                            c["peqGain"] = [0.0, 0.0, 0.0, 0.0]
                        for b in live_session["masterBuses"]:
                            if "geqGain" in live_session["masterBuses"][b]:
                                live_session["masterBuses"][b]["geqGain"] = [0.0]*9

            # Send directly to hardware USB MIDI if not originated from hardware
            if msg.get("source") != "hardware":
                apply_action_to_hardware_midi(msg)

            save_session()
            broadcast_sse(msg, exclude_clientId=client_id)

            resp = json.dumps({"status": "ok"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        super().do_POST()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

# -----------------------------------------------------------------------------
# SERVER RUNNER FUNCTION
# -----------------------------------------------------------------------------
def start_flow8_server(blocking=True):
    midi_engine.scan_and_connect()
    watchdog = threading.Thread(target=midi_watchdog_loop, daemon=True)
    watchdog.start()

    http.server.ThreadingHTTPServer.allow_reuse_address = True
    lan_ips = get_all_ips()

    print("==================================================================")
    print("  BEHRINGER FLOW 8 PRO ROUTER & NATIVE MIDI HUB (v11748 Engine)")
    print(f"  * LOCALHOST DESKTOP APP: http://127.0.0.1:{PORT}")
    print("  * LAN ACCESSIBLE (iPad / Tablets / Phones):")
    for ip in lan_ips:
        print(f"     -> http://{ip}:{PORT}")
    if midi_engine.connected:
        print(f"  * HARDWARE USB MIDI    : {midi_engine.out_name} [ACTIVE]")
    else:
        print("  * HARDWARE USB MIDI    : Waiting for FLOW 8 USB connection...")
    print("==================================================================")

    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Flow8Handler)
    if blocking:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            midi_engine.close()
    else:
        srv_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        srv_thread.start()
        return httpd

if __name__ == "__main__":
    start_flow8_server(blocking=True)
