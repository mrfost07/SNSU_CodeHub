from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    # Register context processor for datetime
    @app.context_processor
    def utility_processor():
        return {'now': datetime}

    # Register blueprints
    with app.app_context():
        from app.auth import bp as auth_bp
        from app.main import bp as main_bp
        from app.projects import bp as projects_bp
        from app.learning import bp as learning_bp
        from app.organizations import bp as organizations_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(projects_bp)
        app.register_blueprint(learning_bp)
        app.register_blueprint(organizations_bp)

    return app
