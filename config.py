class Config ():
    DEBUG=False
    TESTING = False
    UPLOAD_FOLDER = ''
    MAX_CONTENT_LENGTH = 16 *1024 *1024
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = ''




class ProductionConfig (Config):
    pass

class DevelopmentConfig (Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig (Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False
