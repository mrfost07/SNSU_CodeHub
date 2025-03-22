import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Update SQLite configuration
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,
            'timeout': 30
        }
    }
    
    # Enable SQLite foreign key support
    @property
    def SQLALCHEMY_MIGRATE_OPTIONS(self):
        from alembic import context
        from flask import current_app
        with current_app.app_context():
            migrate_options = {
                'compare_type': True,
                'render_as_batch': True,  # Enable batch mode for SQLite
                'compare_server_default': True
            }
            return migrate_options
    
    # Alembic settings for migrations
    ALEMBIC = {
        'script_location': 'migrations',
        'compare_type': True,
        'render_as_batch': True
    }
    
    @staticmethod
    def init_app(app):
        # Create instance directory if it doesn't exist
        os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    
    # Other configs remain the same
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
