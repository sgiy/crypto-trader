import os, sys, json
from Crypto.Cipher import AES
from Crypto import Random

class Protector():
    def __init__(self, password=''):
        self._password = password
        self._iv_length = 16

    def save_encrypted_file(self, dictionary, file_name):
        iv = Random.new().read(self._iv_length)
        cipher = AES.new(self._password, AES.MODE_CFB, iv)
        msg = iv + cipher.encrypt(json.dumps(dictionary))
        print('IV: ', iv)
        file = open(os.path.join(sys.path[0], file_name), 'wb')
        file.write(msg)
        file.close()

    def decrypt_file(self, file_name):
        with open(os.path.join(sys.path[0], file_name), 'rb') as myfile:
            msg=myfile.read()
        iv = msg[:self._iv_length]
        cipher = AES.new(self._password, AES.MODE_CFB, iv)
        return json.loads(cipher.decrypt(msg[self._iv_length:]))
