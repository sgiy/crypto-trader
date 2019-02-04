import os, base64, json
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Protector():
    def __init__(self, password=''):
        self._password = password.encode('utf8')
        self._salt_length = 16

    def generate_key_from_password(self, password, salt = None):
        if salt is None:
            salt = os.urandom(self._salt_length)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return salt, key

    def save_encrypted_file(self, dictionary, full_file_path):
        salt, key = self.generate_key_from_password(self._password)
        f = Fernet(key)
        msg = salt + f.encrypt(str(dictionary).encode('utf8'))

        file = open(full_file_path, 'wb')
        file.write(msg)
        file.close()

    def decrypt_file(self, full_file_path):
        with open(full_file_path, 'rb') as myfile:
            msg=myfile.read()
        salt = msg[:self._salt_length]
        salt, key = self.generate_key_from_password(self._password, salt)
        f = Fernet(key)
        decoded = f.decrypt(msg[self._salt_length:])
        json_acceptable_string = decoded.decode('utf8').replace("'", "\"")
        return json.loads(json_acceptable_string)
