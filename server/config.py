import os

class Config(object):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = b'\xda9$\x9fL\x10\xce\x06`49\xac\x9ar\xeff\xc5K\xd4V\x16$\x16y'
    PORT = 5000

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv('EXIL_SECRET_KEY')
    PORT = 8021
