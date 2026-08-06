# 🖥️ Python Remote Management Framework  
## Client-Server Architecture (Python Proof of Concept)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A Python-based client-server framework built with **Python**, **TCP Socket Programming**, **JSON communication**, and **Tkinter GUI**.

This project demonstrates client-server architecture, bidirectional communication, graphical control interface, network programming concepts, screenshot transfer, file integrity verification, and Python application development.

---

# 🏗️ System Architecture

The project follows a client-server architecture:

```text
                 TCP Communication
                       |
                       |
          +------------+------------+
          |                         |
          v                         v

+--------------------+      +--------------------+
|     Server GUI     |      |       Client       |
|    Controller      |      |    Remote Side     |
+--------------------+      +--------------------+
|                    |      |                    |
| Tkinter Interface  |      | Command Handling   |
| Send Requests      |      | Data Processing    |
| Receive Responses  |      | Screenshot Capture |
| Display Results    |      | File Operations    |
|                    |      |                    |
+--------------------+      +--------------------+
```

## Communication Flow

1. Data is converted into JSON format.
2. Messages are transferred using TCP sockets.
3. XOR-based encoding is used for basic payload obfuscation.
4. A 4-byte length header helps maintain complete message delivery.

---

# 📸 Screenshots & Demo

Visual demonstration of the project interface and main features.

## 🖥️ Server GUI Interface

_Add screenshot here:_

<!-- SERVER_GUI_IMAGE -->

<br>

## 🔗 Client-Server Connection

_Add screenshot here:_

<!-- CLIENT_CONNECTION_IMAGE -->

<br>

## ⚙️ Feature Demonstration

_Add screenshots showing the main features here:_

<!-- FEATURE_IMAGES -->

---

# 📂 Project Structure

```text
tactical-shadow-rat/

├── Server+Victim/
│   ├── server.py          # Server GUI application
│   └── client.py          # Client application
│
├── TrojanClient/
│   ├── victim.exe         # Executable build
│   ├── victim.bat         # Windows launcher
│   ├── image.jpg          # Image resource
│   └── logs.txt           # Log file
│
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
└── .gitignore
```

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/meklon101/tactical-shadow-rat.git
```

## 2. Enter Project Directory

```bash
cd tactical-shadow-rat
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🐧 Kali Linux Setup

For Linux environments install the required GUI packages:

```bash
sudo apt update
```

```bash
sudo apt install python3-tk python3-pil python3-pil.imagetk
```

---

# ⚙️ Configuration

Before running the client, update the server address.

Open:

```text
notepad Server+Victim/client.py
```

Change:

```python
SERVER_HOST = "127.0.0.1"
```

To the server machine IP address:

```python
SERVER_HOST = "IP"
```

The communication port:

```python
SERVER_PORT = 8080
```

---

# ▶️ Running the Project

## Start Server

Open terminal:

```bash
cd Server+Victim
```

Run:

```bash
python server.py
```

The Tkinter management interface will start.

---

## Start Client
Open another terminal:

**Method 1: Using Python (Terminal)**
You can run the client using one of the following methods:

```bash
cd tactical-shadow-rat/TrojanClient
```

Run:

```bash
python victim.py
```
**Method 2: Using the Batch Launcher (Windows)**
Navigate to the `TrojanClient` folder and double-click:
`victim.bat`

After connection, communication can be managed from the server interface.

---

# 💻 Available Commands

The system supports sending operating system commands through the management interface.

## Windows Commands

### Show files and folders

```bash
dir
```

### Display current user

```bash
whoami
```

### Display network configuration

```bash
ipconfig
```

---

## Linux Commands

### List files

```bash
ls -la
```

### Show current directory

```bash
pwd
```

### Display network interfaces

```bash
ip a
```

---

# 🎮 GUI Controls

The management interface includes:

| Control | Description |
|---|---|
| Send Command | Send commands to the connected client |
| Screenshot | Request screenshot capture |
| Keylogger Logs | Retrieve stored log information |
| Get Hash | Calculate SHA-256 checksum |
| TERMINATE | Stop the client process |

---

# 🔐 Security & Communication

The project demonstrates:

- TCP socket communication.
- JSON serialization.
- XOR-based message encoding.
- SHA-256 hashing.
- Client-server data exchange.

---

# 🛠️ Technologies Used

- Python 3
- TCP Socket Programming
- JSON
- Tkinter
- Pillow
- Pynput
- Threading
- Hashlib

---

# 📚 Learning Objectives

This project demonstrates:

- Client-server architecture.
- Network programming.
- Python application development.
- GUI programming.
- Data communication.
- File integrity concepts.

---

# ⚠️ Disclaimer

This project was created for educational purposes only.

Use only in:
- Personal testing environments.
- Authorized laboratories.
- Systems where you have permission.

Unauthorized use on systems without permission is prohibited.

---
