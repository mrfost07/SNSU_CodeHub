from flask import Blueprint

bp = Blueprint('community', __name__, url_prefix='/community')

from app.community import routes
