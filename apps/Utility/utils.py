import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def encryp_file(file_data):
    
    password = b"5JnuwzCE6HoCzcMzoFPjfm02gIp56QU"
    salt = b'\x0cw\xe5\x88\x0b?\x0e\x1f\x0e\xe3\x80\x17n\xfax\xf9'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)

    # เข้ารหัส
    token = f.encrypt(file_data)

    return token


