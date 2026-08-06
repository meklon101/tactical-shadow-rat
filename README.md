🖥️ Python Remote Management Framework (Client-Server Architecture)

""Python" (https://img.shields.io/badge/Python-3.8%2B-blue.svg)" (https://www.python.org/)
""Platform" (https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)"
""License" (https://img.shields.io/badge/License-MIT-green.svg)"

A lightweight cross-platform remote management framework built with Python, TCP Sockets, and Tkinter GUI.

This project demonstrates client-server communication, bidirectional data transfer, remote command execution, screenshot capture, event monitoring, file integrity verification, and graphical control management.

---

📷 Screenshots & Demo

«Add your screenshots here before publishing the project.»

Example:

Controller Dashboard| Client Screenshot
Add image here| Add image here

---

🏗️ System Architecture

The project contains two main components:

┌─────────────────────────┐                 ┌──────────────────────────┐
│    Management Server    │                 │        Remote Client      │
│    (Controller GUI)     │                 │                          │
│                         │                 │                          │
│ • Tkinter Interface     │ <=============> │ • Command Execution      │
│ • Command Management    │   TCP Socket    │ • Screenshot Capture     │
│ • Response Display      │                 │ • File Processing        │
│ • Data Handling         │                 │ • Event Monitoring        │
│                         │                 │                          │
└─────────────────────────┘                 └──────────────────────────┘

---

🔐 Communication Protocol

The system uses the following communication process:

1. Data is converted into JSON format.
2. Messages are transferred through TCP sockets.
3. XOR-based encoding is applied for basic payload obfuscation.
4. A 4-byte length header is added to ensure complete message delivery.

---

🌟 Key Features

💻 Remote Command Execution

Execute system commands remotely and receive real-time output.

📸 Screenshot Capture

Capture screenshots from the connected client and transfer them to the management interface.

⌨️ Keyboard Event Monitoring

Monitor keyboard events and store collected data locally.

🔒 SHA-256 File Integrity Verification

Generate SHA-256 hashes to verify file integrity.

🔄 Connection Management

Maintain communication between client and server and handle connection interruptions.

🖥️ Graphical Control Interface

Interactive Tkinter GUI for managing communication and displaying responses.

---

📂 Project Structure

tactical-shadow-rat/

├── Server+Victim/
│   ├── server.py        # Management Server GUI
│   └── client.py        # Client Application
│
├── TrojanClient/
│   ├── victim.exe       # Executable build
│   ├── victim.bat       # Windows launcher script
│   ├── image.jpg        # Image file
│   └── logs.txt         # Log file
│
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── .gitignore

---

🚀 Installation & Setup

1. Clone Repository

git clone https://github.com/meklon101/tactical-shadow-rat.git

Enter the project folder:

cd tactical-shadow-rat

---

2. Install Dependencies

pip install -r requirements.txt

---

🐧 Kali Linux Setup

Install required GUI packages:

sudo apt update

sudo apt install python3-tk python3-pil python3-pil.imagetk

---

⚙️ Configuration

Before running the client, update the server address:

File:

Server+Victim/client.py

Change:

SERVER_HOST = "127.0.0.1"

To the server machine IP:

SERVER_HOST = "192.168.1.100"

Keep the same port:

SERVER_PORT = 8080

---

▶️ Running the Project

Start Server

Navigate to the server folder:

cd Server+Victim

Run:

python server.py

---

Start Client

Open another terminal:

cd Server+Victim

Run:

python client.py

---

🎮 Available Commands

Examples of system commands:

Windows

dir

List files and folders.

whoami

Display current user information.

ipconfig

Display network configuration.

---

Linux

ls -la

List files and permissions.

pwd

Display current directory.

ip a

Display network interfaces.

---

🔘 GUI Controls

The management interface provides:

Screenshot

Requests and displays a screenshot from the connected client.

Logs

Retrieves stored keyboard event logs.

Hash

Calculates SHA-256 checksum.

Terminate

Stops the client process.

---

🛠️ Technologies Used

- Python 3
- TCP Socket Programming
- JSON
- Tkinter
- Pillow
- Pynput
- Threading
- Hashlib

---

📚 Project Purpose

This project was developed for educational purposes to demonstrate:

- Client-server architecture.
- Network programming.
- Python application development.
- GUI development.
- Security concepts.
- Data communication.

---

⚠️ Disclaimer

This project is intended only for:

- Educational purposes.
- Authorized testing.
- Controlled laboratory environments.

Using this software on systems without permission is prohibited.
