import os

class Config(object):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    # python3 -c 'import os; os.urandom(24).hex()'
    SECRET_KEY = '8c5014adb541158724ee9c580e9699bc892d7f79bed24d98'
    PORT = 5000
    MYSQL_HOST = '192.168.1.240'
    MYSQL_DATABASE = 'exil'
    MYSQL_USER = 'nathan'
    MYSQL_PASSWORD = os.getenv('MYSQL_PI_PASSWORD')

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv('EXIL_SECRET_KEY')
    PORT = 8021
    MYSQL_HOST = 'localhost'
    MYSQL_DATABASE = 'exil'
    MYSQL_USER = 'exil'
    MYSQL_PASSWORD = os.getenv('EXIL_MYSQL_PASSWORD')
