from central_server_files.Constant import SALT
import hashlib

def encrypt(msg: bytes, key: bytes) -> bytes:
    return msg
    # return Fernet(key).encrypt(msg)

def decrypt(msg: bytes, key: bytes) -> bytes:
    return msg
    # return Fernet(key).decrypt(msg)

def hash_and_salt(password: str) -> str:
    hasher = hashlib.sha256((SALT+password).encode())
    return hasher.hexdigest()
