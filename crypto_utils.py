import base64
import os
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# Standard salt for local derivation (or load dynamic salt)
SALT = b'passvault_static_salt_32bytes_len' 

def generate_key(master_password: str) -> bytes:
    """Derives a strict 32-byte (256-bit) raw binary key from master password."""
    return PBKDF2(master_password, SALT, dkLen=32, count=100000)

def encrypt_data(plain_text: str, key: bytes) -> str:
    """Encrypts text using AES-256 GCM / CBC mode."""
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))
    
    # Store nonce + tag + ciphertext as Base64 string
    combined = cipher.nonce + tag + ciphertext
    return base64.b64encode(combined).decode('utf-8')

def decrypt_data(encrypted_b64: str, key: bytes) -> str:
    """Decrypts Base64 ciphertext back into plain text string."""
    combined = base64.b64decode(encrypted_b64.encode('utf-8'))
    
    nonce = combined[:16]
    tag = combined[16:32]
    ciphertext = combined[32:]
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted_bytes.decode('utf-8')