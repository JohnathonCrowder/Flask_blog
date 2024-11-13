import os

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  # Change this to a secure secret key