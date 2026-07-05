import json
import os
import base64
import sys
import socket
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureConfig:
    def __init__(self):
        self.app_name = "UltraDownloader"
        self.app_data = os.getenv('APPDATA')
        self.config_dir = os.path.join(self.app_data, self.app_name)
        self.config_file = os.path.join(self.config_dir, "secure_config.bin")
        self.key_file = os.path.join(self.config_dir, ".config_key")
        self._ensure_directories()
        
    def _ensure_directories(self):
        os.makedirs(self.config_dir, exist_ok=True)
        
    def _get_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            system_info = f"{socket.gethostname()}{getpass.getuser()}{sys.platform}".encode()
            salt = b'UltraDownloaderSalt2024'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(system_info))
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
    
    def save_config(self, config_data):
        key = self._get_or_create_key()
        fernet = Fernet(key)
        json_data = json.dumps(config_data).encode()
        encrypted_data = fernet.encrypt(json_data)
        with open(self.config_file, 'wb') as f:
            f.write(encrypted_data)
    
    def load_config(self):
        if not os.path.exists(self.config_file):
            return None
        try:
            key = self._get_or_create_key()
            fernet = Fernet(key)
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception:
            return None