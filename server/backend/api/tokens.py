from flask import jsonify, g
from backend import db
from backend.api import api
from backend.api.auth import basic_auth
from backend.api.auth import token_auth


@api.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    print("token: " + token)
    return jsonify({'token': token})


@api.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204

