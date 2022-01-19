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


def decryp_file(file_data):
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

    decryp_data = f.decrypt(file_data)
    return decryp_data


def thai_date(date, mode='basic'):
    result = "d m y"
    th_day = date.day
    th_weekday = ['อา.','จ.','อ.','พ.','พฤ.','ศ.','ส.'][date.weekday()]
    th_month = ['ผิดพลาด', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'][date.month]
    th_year = (date.year + 543) % 100
    if mode == 'basic':
        retult = f"{th_day} {th_month}{th_year}"
        return retult
    if mode == 'wd-short':
        retult = f"{th_weekday} ที่ {th_day} {th_month}{th_year}"
        return retult
    return result
    
