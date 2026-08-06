# Python Remote Management Framework

## Project Summary

Python Remote Management Framework is a Python-based remote access tool built with a client-server architecture. It provides remote command execution, keystroke capture, screen capture, and file identification features while maintaining connection resilience and basic traffic obfuscation.

---

## Overview

This project demonstrates a remote administration and intelligence-gathering solution implemented over TCP. The system is designed to maintain stable connectivity, recover automatically from disconnections, and conceal its victim-side activity behind a cover image.

---

## Key Features

- **Attacker GUI:** Tkinter-based interface with real-time logs, command input, and quick access buttons.
- **Secure Transport:** TCP sockets for reliable data delivery.
- **Traffic Obfuscation:** XOR-based encryption of JSON messages.
- **Auto-Reconnect:** Victim client reconnects automatically after a dropped connection.
- **Keylogger:** Collects keyboard input and stores it in `logs.txt`.
- **Remote Shell:** Executes arbitrary commands on the victim machine and returns output.
- **Screenshot Capture:** Captures the victim screen, encodes it in Base64, and sends it to the server.
- **File Hashing:** SHA-256 file fingerprinting for content-based identification and integrity checking.

---

## Architecture

The repository includes two main components:

- `server.py` — attacker-side controller that listens for connections and sends commands.
- `client.py` — victim-side Trojan client that connects to the server, receives instructions, and executes actions.

The communication layer transmits encrypted JSON payloads with a fixed XOR key. The client maintains a background keylogger thread and attempts to reconnect on network failure.

---

## Trojan Packaging

The victim client is designed to run as a Trojan-style executable concealed with a cover image. 
When launched, a sample image automatically opens on the screen as a **visual decoy** to mislead the user into thinking a normal picture was opened, while the RAT code silently establishes a background TCP connection to the server.
---

## Installation

### Requirements

- Python 3.8 or newer
- Python libraries:
  - `pynput`
  - `Pillow`

### Setup

```bash
pip install pynput pillow
```

---

## Usage

1. Configure the server address and port in `client.py`:
   - `SERVER_HOST = "SERVER_IP"` *(Use your server IP, or "127.0.0.1" for local testing)*
   - `SERVER_PORT = 8080`
2. Start the server:

```bash
python server.py
```

3. Start the client on the target machine:

```bash
python client.bat
```

4. Control the client from the GUI:
   - `Screenshot` — capture and display screen image
   - `Keylogger Logs` — retrieve saved keystrokes
   - `Get Hash (logs.txt)` — compute SHA-256 digest for the log file
   - `TERMINATE` — disconnect client
   - Custom shell command entry — execute arbitrary commands remotely

---

## Repository Files

- `client.py`
- `server.py`
- `README.md`
