import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'postgresql://flask_blog_database_wga3_user:guJZJtM65lfBcbRY40c7dYAckBGnBfuP@dpg-ct925td6l47c73am13j0-a.ohio-postgres.render.com/flask_blog_database_wga3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB max file size