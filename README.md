# Tactical Shadow RAT

This repository contains a complete proof-of-concept remote access tool project. It includes the client and server components, the decoy image, and an example victim executable.

## Project structure

- `TrojanClient/`
  - `victim.exe` - compiled executable for the victim side.
  - `victim.bat` - batch file for starting the executable.
  - `image.jpg` - decoy image displayed on the victim machine.
  - `logs.txt` - keystroke log file that the client writes to.
- `Server+Victim/`
  - `client.py` - Python source code for the client. This code opens the decoy image, connects back to the server, handles commands, and returns results.
  - `server.py` - Python source code for the server GUI. It listens for the client connection and sends commands.

## Full project workflow

### 1. Start the server

The server is the controller application. It listens for an incoming connection from the client and shows a GUI for commands.

- Install Python and required packages:
  ```powershell
  pip install pynput pillow
  ```
- Start the server:
  ```powershell
  python "Server+Victim\server.py"
  ```

The server GUI will open and wait for the client to connect.

### 2. Run the victim executable

The victim side runs from `TrojanClient`.

- Place `victim.exe`, `victim.bat`, and `image.jpg` together.
- Run `victim.exe` or double-click `victim.bat`.

On startup, the client code opens `image.jpg` to appear as a normal image view.

### 3. Client connects back to server

The client in `client.py` contains the server address configuration:

- `SERVER_HOST` - the server IP address.
- `SERVER_PORT` - the server port.

After opening the image, the client repeatedly attempts to connect to the server. When the server accepts the connection, the client waits for commands.

### 4. Server commands and client behavior

The server sends encrypted JSON messages to the client. The client decodes and handles these actions:

- `screencap`
  - The client takes a screenshot and sends it back as a Base64 image.
- `keylog`
  - The client reads `logs.txt` and returns the stored keystrokes.
- `hash`
  - The client calculates SHA256 for the requested file and returns the hash.
- `terminate`
  - The client closes the connection and exits.
- Any other command string
  - The client executes it in a shell and returns the command output.

### 5. What the server shows

The server GUI shows the client responses in a text window. It also opens a new image window whenever a screenshot is received.

## What to upload to GitHub

Upload the full project root with both folders and the main README:

- `README.md` (this file)
- `TrojanClient/`
  - `victim.exe`
  - `victim.bat`
  - `image.jpg`
  - `logs.txt` (optional)
- `Server+Victim/`
  - `client.py`
  - `server.py`

This makes the project clear for others: they will see the source code, the victim files, and the full execution flow.

## Important notes

- The key source code files are `Server+Victim/client.py` and `Server+Victim/server.py`.
- `victim.exe` is the compiled executable. The actual source is in `client.py`.
- Keep the README general and not personal.

## Example upload instructions

To upload using GitHub web upload, drag these items into the repository:

- `README.md`
- `TrojanClient/` folder
- `Server+Victim/` folder

If you prefer Git commands, use:

```powershell
cd "C:\פרויקטים ITSAFE\RAT shadow"
git init
git add .
git commit -m "Add Tactical Shadow RAT full project"
git remote add origin https://github.com/meklon101/tactical-shadow-rat.git
git branch -M main
git push -u origin main
```

## Disclaimer

This repository is a demonstration of a remote access tool concept. It is not intended for unauthorized use.
