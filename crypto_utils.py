import os
import base64
import hashlib
from Crypto.Cipher import AES 
from Crypto.Util.Padding import pad, unpad

def generate_key(master_password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)

    key = hashlib.pbkdf2_hmac(
        hash_name = 'sha256',
        password = master_password.encode('utf-8'),
        salt = salt,
        iterations = 600000,
        dklen = 32
    )
    return key, salt

def encrypt_data(data: str, key: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(iv + encrypted_bytes)

def decrypt_data(encrypted_base64: bytes, key: bytes) -> str:
    raw_data = base64.b64decode(encrypted_base64)
    iv = raw_data[:16]
    encrypted_bytes = raw_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_padded, AES.block_size).decode('utf-8')
