from flask import Flask
from flask_login import LoginManager
from .models import db
from config import Config

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .routes import main
    from .auth import auth
    from .blog import blog

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(blog)

    with app.app_context():
        db.create_all()

    return app