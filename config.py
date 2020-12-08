import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SUPER-SECRET'
    LOGFILE = "log.log"
    SQLALCHEMY_DATABASE_URI = 'postgresql://moonstrider:123@localhost/site3'

    AVAILABLE_DATAENTRIES = ['mood', 'efficiency', 'imagination', 'diary']
    DAY_DISPLAY_MAX = 5
    WEEKS_DISPLAY_MAX = 20
    MONTHS_DISPLAY_5_MAX = 40
    MONTHS_DISPLAY_10_MAX = 65
    LIFESPAN = 80



class DevConfig(Config):
    DEBUG = True
    LOG_BACKTRACE = True
    LOG_LEVEL = 'DEBUG'

class ProdConfig(Config):
    LOG_BACKTRACE = False
    LOG_LEVEL = 'INFO'

config = {'default': DevConfig,
          'DevConfig': DevConfig,
          'ProdConfig': ProdConfig}