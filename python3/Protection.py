import base64
import hashlib
import json
import os

from cryptography.fernet import Fernet


class Protector:
    def __init__(self, password=''):
        self._password = password.encode('utf8')
        self._salt_length = 16

    def generate_key_from_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(self._salt_length)
        key = base64.urlsafe_b64encode(
                hashlib.pbkdf2_hmac(
                    'sha256',
                    password,
                    salt,
                    1000000
                )
            )
        return salt, key

    def save_encrypted_file(self, dictionary, full_file_path):
        print("Encrypting settings...")
        salt, key = self.generate_key_from_password(self._password)
        f = Fernet(key)
        msg = salt + f.encrypt(str(dictionary).encode('utf8'))

        file = open(full_file_path, 'wb')
        file.write(msg)
        file.close()
        print("Settings are saved")

    def decrypt_file(self, full_file_path):
        print("Unlocking settings...")
        with open(full_file_path, 'rb') as file_contents:
            msg = file_contents.read()
        salt = msg[:self._salt_length]
        salt, key = self.generate_key_from_password(self._password, salt)
        f = Fernet(key)
        decoded = f.decrypt(msg[self._salt_length:])
        json_acceptable_string = decoded.decode('utf8').replace("'", "\"")
        print("Settings are unlocked")
        return json.loads(json_acceptable_string)
