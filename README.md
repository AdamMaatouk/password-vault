# PassVault

A secure, multi-platform local password manager and 2FA authenticator with 256-bit AES encryption. Available as a Flutter mobile application (Android) and a CustomTkinter desktop application (Windows).

![Flutter](https://img.shields.io/badge/Flutter-3.0+-02569B?logo=flutter)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📱 PassVault Mobile (Android)

Built with Flutter, PassVault Mobile provides a responsive, dark-themed experience for local credential management and two-factor authentication on the go.

### Mobile Features
* **256-bit AES Vault Encryption:** Hardware-backed encrypted storage with PBKDF2 key salting (`cryptography` & `flutter_secure_storage`).
* **Built-in 2FA Authenticator:** Integrated TOTP code generator for two-factor authentication.
* **Camera QR Scanner:** Instant secret key import using live camera scanning (`mobile_scanner`).
* **Biometric Authentication:** Quick and secure vault unlock via Fingerprint / Face ID (`local_auth`).
* **Adaptive Launcher Icon:** Native Android adaptive icon support.

### Download & Install (Android)
1. Go to the latest **[PassVault Mobile v1.0.0 Release](../../releases/latest)** page.
2. Download `PassVault.apk`.
3. Open the file on your Android device and allow **Install from unknown sources** if prompted.

---

## 💻 PassVault Desktop (Windows)

A standalone Windows application engineered with Python and CustomTkinter for offline credential protection.

### Desktop Features
* **Local AES-256 Storage:** Derives encryption keys via PBKDF2 HMAC-SHA256 and encrypts data locally on disk using PyCryptodome.
* **Modern GUI:** Clean dark-mode interface with password generation and category tracking.
* **Zero External Calls:** Runs 100% offline without third-party cloud servers.

### Download & Run (Windows)
1. Go to the **[PassVault Desktop v1.0.1 Release](../../releases/tag/v1.0.1)** page.
2. Download `PassVault.exe`.
3. Run the executable directly on Windows.

---

## 🛠️ Building From Source

Clone the repository:
```bash
git clone [https://github.com/AdamMaatouk/password-vault.git](https://github.com/AdamMaatouk/password-vault.git)
cd password-vault
