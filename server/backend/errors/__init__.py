from flask import Blueprint

err = Blueprint('errors', __name__)

from backend.errors import errors
