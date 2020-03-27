class Config(object):
    DEBUG = False
    MONGO_URI = 'mongodb://localhost:27017/exil'

class DevelopmentConfig(Config):
    pass

class ProductionConfig(Config):
    pass
