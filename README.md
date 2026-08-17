# PassVault

A lightweight Windows desktop application for managing passwords locally with 256-bit AES encryption.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Overview
PassVault is a standalone password manager built with Python and CustomTkinter. It encrypts your credentials locally before saving them to disk, ensuring your vault remains private without relying on third-party cloud services or external servers.

## Key Features
* **AES-256 Encryption:** Derives secure keys using PBKDF2 HMAC-SHA256 and encrypts storage via PyCryptodome.
* **Modern GUI:** Built with CustomTkinter for a clean, responsive dark-mode layout.
* **Master Password Safeguard:** Vault reset options safely clear local data if you forget your master password.
* **Zero External Calls:** Storage runs entirely offline on your device (`vault.json`).

## Download & Run
You can download the pre-compiled `.exe` file directly without needing Python installed:

1. Go to the **[PassVault v1.0.1 Release](../../releases/tag/v1.0.1)** page.
2. Download `PassVault.exe`.
3. Run the executable on Windows.

## Running from Source

### 1. Prerequisites
Make sure you have Python installed, then clone the repository:
```bash
git clone [https://github.com/AdamMaatouk/password-vault.git](https://github.com/AdamMaatouk/password-vault.git)
cd password-vault
