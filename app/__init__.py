from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db, User
from config import Config
from .admin import admin
from . import commands
from .models import SiteSettings
from .blog import blog, timeago  # Import the timeago function

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Specify the login route
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'

migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes import main
    from .auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(blog)
    app.register_blueprint(admin)

    # Initialize CLI commands
    commands.init_app(app)

    # Register the timeago template filter
    app.template_filter('timeago')(timeago)

    # Context processor to inject settings into all templates
    @app.context_processor
    def inject_settings():
        settings = SiteSettings.query.first()
        return dict(site_settings=settings)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app