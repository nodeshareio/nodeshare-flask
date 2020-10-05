from flask import Blueprint


site = Blueprint('site', __name__,)

from backend.site import routes, events

