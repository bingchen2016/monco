from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    """ Construct the core app object. """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        # Import parts of our application
        from .profile import profile
        from .auth import auth
        from .admin import admin

        # Register Blueprints
        app.register_blueprint(profile.profile_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(admin.admin_bp)

        # Create Database Models
        db.create_all()

        return app
