from flask import Blueprint

bp = Blueprint('learning', __name__)

from app.learning import routes
