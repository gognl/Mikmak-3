
def xor(b1: bytes, b2: bytes):
    return bytes(a ^ b for a, b in zip(b1, b2))

def encrypt(msg: bytes, key: bytes) -> bytes:
    return xor(msg, key*(len(msg)//len(key)+1))

def decrypt(msg: bytes, key: bytes) -> bytes:
    return xor(msg, key*(len(msg)//len(key)+1))

