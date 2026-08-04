# Tactical Shadow RAT

This repository contains a proof-of-concept remote access tool (RAT) project with both the attacker-side controller and the victim-side payload.

## Repository structure

- `TrojanClient/`
  - `victim.exe` - compiled victim payload executable.
  - `victim.bat` - wrapper to launch the Python payload.
  - `image.jpg` - decoy image displayed to the victim.
  - `logs.txt` - local keystroke log file written by the client.
- `Server+Victim/`
  - `client.py` - Python source code for the victim client.
  - `server.py` - Python source code for the attacker GUI controller.
- `.gitignore` - ignores local caches, temp files, and editor artifacts.

## Overview

This project demonstrates a client-server remote access model with the following capabilities:

- Remote shell command execution
- Screenshot capture
- Keystroke logging
- SHA-256 file hashing
- Automatic reconnection from the victim to the controller
- Simple XOR-based payload obfuscation for JSON messages

## Prerequisites

- Python 3.8 or later
- Install required Python packages:
  ```powershell
  pip install pynput pillow
  ```

## Configuration

### Client configuration

Open `Server+Victim/client.py` and update the server address:

```python
SERVER_HOST = "SERVER_IP"
SERVER_PORT = 8080
```

Replace `SERVER_IP` with the actual IP address of the machine running `Server+Victim/server.py`.

### Server configuration

The attacker server listens on port `8080` by default. If needed, modify `LISTEN_PORT` in `Server+Victim/server.py`.

## How to run

### Start the server

From the repository root:

```powershell
python "Server+Victim\server.py"
```

### Start the victim client

From the `TrojanClient` folder, run:

```powershell
python "victim.bat"
```

or use the compiled `victim.exe` payload.

## Behavior

### Server commands

The server sends encrypted JSON actions to the client:

- `screencap` — capture a screenshot and return it encoded in Base64
- `keylog` — send back the contents of `logs.txt`
- `hash` — compute SHA-256 for the requested file
- `terminate` — close the connection and exit the client
- Any other string — execute it as a shell command and return stdout/stderr

### Client behavior

The victim client:

- opens `image.jpg` as a decoy window
- connects back to the server on startup
- maintains a background keylogger thread
- reconnects automatically if the server is unavailable
- sends encrypted messages to the server using XOR obfuscation

## Professional adjustments made

- Removed Hebrew comments and local path references from source files
- Replaced hard-coded IP addresses with a reusable placeholder (`SERVER_IP`)
- Added `.gitignore` to ignore runtime and editor artifacts
- Standardized the documentation for a cleaner GitHub presentation

## Notes

- `victim.exe` is the precompiled payload; `client.py` contains the actual source logic.
- Do not deploy this code on unauthorized systems. Use it only in controlled test environments.

## GitHub upload guidance

The repository already contains the necessary project files. If you want to publish the current state, run:

```powershell
cd "C:\path\to\RAT shadow"
git add .
git commit -m "Clean project structure and documentation"
git push origin main
```
