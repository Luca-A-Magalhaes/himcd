import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SEND_FILE_MAX_AGE_DEFAULT = 0
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/translations/')
    LANGUAGES = ['es', 'pt_BR', 'fr', 'en']
    DB_HOST = os.environ.get('DB_HOST') or '127.0.0.1'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PORT = os.environ.get('DB_PORT') or '3306'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'root'
    DB_NAME = os.environ.get('DB_NAME') or 'himcd'
    SQLALCHEMY_DATABASE_URI = (f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
