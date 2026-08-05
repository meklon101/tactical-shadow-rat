# 🖥️ Remote Management & Administration Tool (Python Proof-of-Concept)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20(Kali)-lightgrey.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

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
'''
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

'''Bash
pip install -r requirements.txt
'''
'''
pip install -r requirements.txt
'''
