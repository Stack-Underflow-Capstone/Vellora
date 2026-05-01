import json
from app.config import settings
from cryptography.fernet import Fernet

f = Fernet((settings.FERNET_KEY).encode())

def encrypt_address(address: str) -> str:
    if not address:
        return ""
    return f.encrypt(address.encode()).decode()

def decrypt_address(token: str) -> str:
    if not token:
        return ""
    return f.decrypt(token.encode()).decode()

def encrypt_geometry(geometry: dict) -> str:
    if not geometry:
        return ""
    #convert dict to string then encrypt it
    geometry_json = json.dumps(geometry, separators=(',', ':'))
    return f.encrypt(geometry_json.encode()).decode()

def decrypt_geometry(encrypted_geometry: str) -> dict:
    if not encrypted_geometry:
        return {}
    #decrypt the str then revert back to dict
    decrypted_json = f.decrypt(encrypted_geometry.encode()).decode()
    return json.loads(decrypted_json)