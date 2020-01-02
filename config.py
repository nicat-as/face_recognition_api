class Config ():
    DEBUG=False
    TESTING = False
    UPLOAD_FOLDER = '/home/nicat/Documents/paper/face_recognition_api/downloads'
    MAX_CONTENT_LENGTH = 16 *1024 *1024
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://nicat:Access2@mysqldb@68.183.66.167:3306/nicat'




class ProductionConfig (Config):
    pass

class DevelopmentConfig (Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig (Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False