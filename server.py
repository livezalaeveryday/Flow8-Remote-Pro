import http.server
import socket
import os
import sys
import json
import time
import threading
import queue

PORT = 8844
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(DIRECTORY, "live_session.json")

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
        "fx1": {"presetIdx": 0, "param1": 50, "param2Idx": 0, "mute": False},
        "fx2": {"presetIdx": 0, "param1": 50, "param2Idx": 0, "tempoMs": 500, "mute": False}
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
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Silence console log spam for SSE and continuous fader streaming
        pass

    def do_GET(self):
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

            # Initial greeting event
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

                    # Keep-alive heartbeat every 15 seconds
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

        # Fallback to standard static files
        super().do_GET()

    def do_POST(self):
        # Handle Action / MIDI updates from Localhost or LAN clients
        if self.path == "/api/action":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            try:
                msg = json.loads(body.decode("utf-8"))
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {e}")
                return

            # Apply to master live session
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

                elif action == "setEqBand":
                    ch = msg.get("channel", 0)
                    bIdx = msg.get("bandIndex", 0)
                    gain = float(msg.get("gain", 0.0))
                    if 0 <= ch < len(live_session["channels"]):
                        live_session["channels"][ch]["peqGain"][bIdx] = gain

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

            # Save in background
            save_session()

            # Broadcast to all other screens!
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
# MAIN SERVER ENTRYPOINT
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    os.chdir(DIRECTORY)
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    lan_ips = get_all_ips()
    primary_lan = lan_ips[0] if lan_ips else "127.0.0.1"

    print("==================================================================")
    print("  BEHRINGER FLOW 8 PRO ROUTER & SESSION HUB (v11748 Engine)")
    print(f"  ★ LOCALHOST (Master Direct Web MIDI): http://localhost:{PORT}")
    print("  ★ LAN ACCESSIBLE (iPad / Tablets / Phones):")
    for ip in lan_ips:
        print(f"     -> http://{ip}:{PORT}")
    print("  ★ Real-Time SSE Hub & Hardware Session Persistence Active")
    print("==================================================================")

    try:
        with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Flow8Handler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")
