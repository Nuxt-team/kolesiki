import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

def generate_secret_key():
    base_string = "kolesiki_shop_2024_secure"
    hash_object = hashlib.sha256(base_string.encode())
    return hash_object.hexdigest()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or generate_secret_key()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://kolesiki_user:your_password@localhost:5432/kolesiki_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False