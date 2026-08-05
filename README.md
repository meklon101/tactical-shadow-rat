# 🖥️ Remote Management & Administration Tool (Python Proof-of-Concept)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://github.com/meklon101/tactical-shadow-rat)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20(Kali)-lightgrey.svg)](https://github.com/meklon101/tactical-shadow-rat)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/meklon101/tactical-shadow-rat)

A lightweight, cross-platform Remote Administration Tool (RAT) architecture built with **Python**, **TCP Sockets**, and a **Tkinter Graphical User Interface (GUI)**. 

This project demonstrates how client-server systems handle bidirectional data flow, custom obfuscation, remote shell execution, and live event monitoring across Windows and Linux environments.

---

## 📷 Screenshots & Demo

> *Add your demonstration screenshots below before sharing on LinkedIn:*

| Controller Dashboard (GUI) | Client Screenshot Capture |
| :---: | :---: |
| ![Controller Interface](docs/dashboard.png) | ![Captured Screen](docs/screenshot_demo.png) |

---

## 🏗️ How the System Works

The framework consists of two primary components communicating over encrypted TCP sockets:

```text
  ┌─────────────────────────┐                     ┌──────────────────────────┐
  │   Management Server     │                     │       Remote Client      │
  │   (Controller GUI)      │ <=== Encrypted ===> │     (Target System)      │
  │                         │      TCP Stream     │                          │
  │ • Real-time Output Log  │     (Port 8080)     │ • Shell Execution        │
  │ • Quick Control Panel   │                     │ • Screenshot Capture     │
  │ • Image Render Engine   │                     │ • Keystroke Monitoring   │
  └─────────────────────────┘                     └──────────────────────────┘
🔐 Communication & Data Flow Protocol
JSON Serialization: Commands and exfiltrated data are packaged into standard JSON objects.

XOR Encryption: Messages are obfuscated on-the-fly using a symmetric byte-level XOR mechanism (KEY = b'simple_xor_key').

4-Byte Length Header: Packets are prepended with a 4-byte big-endian integer header indicating payload size, ensuring complete packet reassembly across TCP chunks without stream corruption.   

🌟 Key Features
💻 Interactive Remote Shell: Execute system terminal commands (e.g., whoami, ipconfig, ls -la) remotely with real-time feedback.   

📸 Cross-Platform Screenshot Capture: Uses the high-performance mss library to capture primary displays seamlessly on Windows and Linux (Base64 encoded).   

⌨️ Keystroke Log Collection: Background monitoring using pynput with thread-safe file handling (log_lock).   

🔒 Data Integrity Check: On-demand SHA-256 hash calculation (hashlib) to verify log file integrity.   

🔄 Resilient Reconnection Loop: Built-in exponential backoff retry mechanism preventing client failure during network drops.   

🖥️ Operator GUI Panel: Interactive Tkinter control board with automatic image scaling via PIL/Pillow.   

📂 Project Structure
Plaintext
tactical-shadow-rat/
├── Server+Victim/
│   ├── server.py       # Management Controller GUI (Runs on Kali Linux / Windows)
│   └── client.py       # Remote Agent Client (Runs on Target Host)
├── TrojanClient/
│   ├── victim.exe      # Executable launcher build
│   ├── victim.bat      # Windows batch script wrapper
│   ├── image.jpg       # Decoy display image
│   └── logs.txt        # Keystroke store
├── .gitignore          # Ignores temp caches and screenshots
├── README.md           # Documentation & Architecture Overview
└── requirements.txt    # Python dependencies
🚀 Setup & Installation Guide
1. Install Dependencies
Install required Python modules:   

Bash
pip install -r requirements.txt
🐧 Additional Setup for Kali Linux (Server Host):
Because Tkinter and PIL display bindings are packaged separately in Linux repositories, run the following command before starting the server:   

Bash
sudo apt update
sudo apt install -y python3-tk python3-pil python3-pil.imagetk
2. Configuration
Before running, update the network connection settings in Server+Victim/client.py:   

Python
# Set SERVER_HOST to your Controller IP address (e.g., Kali Linux IP)
SERVER_HOST = "192.168.1.100"
SERVER_PORT = 8080
3. Execution Steps
Step 1: Start the Controller (Server)
Launch the GUI interface:   

Bash
python "Server+Victim/server.py"
Step 2: Run the Remote Agent (Client)
Execute the client script on the remote host:   

Bash
python "Server+Victim/client.py"
🎮 Controller Dashboard Controls
Command Entry Box: Type any OS command and press Enter or click Send Command.

💻 Executing Remote System Commands (Examples)
You can run any native system command directly from the GUI entry field. Output from the client is captured via subprocess and streamed back live to the console window:

Target OS	Command	Description & Purpose
Windows	dir	List all files, folders, and directories in the current path.
Windows	whoami	Check current logged-in user and privilege levels.
Windows	ipconfig /all	View network interfaces, IP addresses, and DNS configuration.
Windows	tasklist	View all active running processes on the host.
Linux (Kali)	ls -la	List all files and directories (including hidden files & permissions).
Linux (Kali)	pwd	Print the current working directory path.
Cross-Platform	ping -c 4 8.8.8.8	Test internet and network connectivity from the client side.
💡 Note: Commands are executed non-interactively. Avoid commands that require interactive user input (e.g., powershell or nano).

Screenshot Button: Requests a screen capture. The incoming image is automatically decoded, saved under screenshots/, and displayed in a popup window.

Keylogger Logs Button: Exfiltrates accumulated keystroke data.

Get Hash Button: Calculates and returns the SHA-256 checksum of logs.txt.

TERMINATE Button: Sends a graceful termination command to shutdown the remote agent process.

⚠️ Disclaimer
Educational and Authorized Testing Only

This software is created solely for educational purposes, architecture research, and authorized security assessments. Deploying or executing this tool against systems without explicit, mutual written authorization is strictly prohibited.
