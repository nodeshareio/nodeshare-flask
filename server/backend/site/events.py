from flask import session, request, jsonify
from flask_socketio import emit
from flask_login import current_user
from .. import socketio


@socketio.on('connect', namespace='/site')
def connect():
    if current_user.is_authenticated:
        print(current_user.username)
        emit('set_username', {'msg': current_user.username})
    else:
        return False