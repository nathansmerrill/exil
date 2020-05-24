import os

class Config(object):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = '8c5014adb541158724ee9c580e9699bc892d7f79bed24d98'
    PORT = 5000

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv('EXIL_SECRET_KEY')
    PORT = 8021
