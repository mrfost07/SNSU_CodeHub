from flask import Blueprint

bp = Blueprint('organizations', __name__)

from app.organizations import routes
