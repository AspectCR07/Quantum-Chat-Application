# Quantum Secure Chat Application

A secure chat application demonstrating the principles of Quantum Key Distribution (QKD) using the BB84 protocol.

## Overview

This application provides a chat interface where messages are encrypted and decrypted using secure keys generated via simulated quantum processes. It emphasizes dynamic security with features like continuous key renewal and live eavesdropping detection.

## Features

*   **BB84 Protocol:** Implements the BB84 quantum key distribution protocol to establish secure communication.
*   **Continuous Key Renewal:** A fresh quantum key is generated for every single message sent, ensuring perfect forward secrecy.
*   **Eavesdropping Detection:** Monitors the quantum channel error rate. If an eavesdropper is detected mid-chat causing the error rate to exceed the safe threshold, the key exchange is aborted and the users are alerted.
*   **Quantum Visualizations:** Includes visual representations of the quantum circuits using Qiskit to help understand the underlying mechanics.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AspectCR07/Quantum-Chat-Application.git
    cd Quantum-Chat-Application
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Start the application by running:
```bash
python app.py
```
