from flask import Blueprint

admin = Blueprint('admin', __name__)

from backend.admin import routes
