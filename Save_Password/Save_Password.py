"""
This file is used to parse save password JSON files.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Save_Password():
    def __init__(self, password_object, address, remarks, password, encryption = True):
        self.password_object = password_object
        self.address = address
        self.remarks = remarks
        self.password = password
        self.encryption = encryption
        self.content = {password_object:}