class Config(object):
    DEBUG = False
    MONGO_URI = 'mongodb://localhost:27017/exil'

class DevelopmentConfig(Config):
    SECRET_KEY = b'\xda9$\x9fL\x10\xce\x06`49\xac\x9ar\xeff\xc5K\xd4V\x16$\x16y'

class ProductionConfig(Config):
    @property
    def SECRET_KEY(self):
        import sys
        sys.path.append('/home/merrilln/pythonbin')
        from flaskSecretKeys import EXIL_SECRET_KEY
        return EXIL_SECRET_KEY
