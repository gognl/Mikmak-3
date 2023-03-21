from central_server_files.Constant import abaaababaab
import hashlib

def xor(b1: bytes, b2: bytes):
    return bytes(a ^ b for a, b in zip(b1, b2))

def encrypt(msg: bytes, key: bytes) -> bytes:
    return xor(msg, key*(len(msg)//len(key)+1))

def decrypt(msg: bytes, key: bytes) -> bytes:
    return xor(msg, key*(len(msg)//len(key)+1))

def hash_and_salt(password: str) -> str:
    hasher = hashlib.sha256((abaaababaab+password).encode())
    return hasher.hexdigest()
