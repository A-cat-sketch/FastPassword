"""
Vault manager
"""

import os
import json
from argon2.low_level import hash_secret_raw, Type
from Save_Password import PasswordEntry
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class VaultManager():
    """
    Vault manager class
    """
    def __init__(self, filepath, main_password):
        self.filepath = filepath
        self.main_password = main_password.encode('utf-8')

    def _get_key(self, salt=None):
        if salt is None:
            salt = os.urandom(16)
        key = hash_secret_raw(
        secret=self.main_password,
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID
    )
        return key, salt
    def _get_json(self, name, address, remarks, password):
        pwd_et = PasswordEntry.PasswordEntry(name=name, address=address, remarks=remarks, password=password)
        return json.dumps(pwd_et.to_dict(), ensure_ascii=False)

    def have_lock(self, name, address, remarks, password):
        key,salt = self._get_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, self._get_json(name, address, remarks, password).encode("utf-8"), None)
        return salt+nonce+ciphertext

    def get_password(self, row_data):
        salt = row_data[:16]
        nonce = row_data[16:28]
        ciphertext = row_data[28:]
        
        key, _ = self._get_key(salt)
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)

        json_str = decrypted.decode("utf-8")
        data_dict = json.loads(json_str)
        
        return data_dict