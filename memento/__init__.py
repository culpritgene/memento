import logging

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from loguru import logger

from config import config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'user_bp.login'
login_manager.login_message_category = 'info'

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())

def create_app():
    app = Flask(__name__)
    app.config.from_object(config['DevConfig'])

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    logger.start(app.config['LOGFILE'], level=app.config['LOG_LEVEL'], format="{time} {level} {message}",
                 backtrace=app.config['LOG_BACKTRACE'], rotation='20 MB')

    # we are using loguru as simple logger
    app.logger.addHandler(InterceptHandler())


    with app.app_context():
        from .home.routes import home_bp
        from .users.routes import user_bp
        from .dashapp.matrix import init_dash
        from .dashapp.routes import matrix_bp, url_base

        app.register_blueprint(home_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(matrix_bp)

        app = init_dash(app, url_base)
        try:
            db.create_all()  ### TODO: move ?
        except ValueError:
            pass

    return app

