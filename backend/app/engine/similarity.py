import hashlib

def file_signature(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def similarity(sig1, sig2):
    return 1.0 if sig1 == sig2 else 0.5