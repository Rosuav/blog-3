import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql:///blogful"
    DEBUG = True
    SECRET_KEY = os.environ.get("RANDOM_KEY_TO_REPLACE", os.random(12))