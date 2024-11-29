from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db, User
from config import Config
from .admin import admin
from . import commands
from .models import SiteSettings
from .blog import blog, timeago  # Import the timeago function

login_manager = LoginManager()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'

    from .routes import main
    from .auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(blog)
    app.register_blueprint(admin)

    commands.init_app(app)

    # Register the timeago template filter
    app.template_filter('timeago')(timeago)

    @app.context_processor
    def inject_settings():
        settings = SiteSettings.query.first()
        return dict(site_settings=settings)

    return app