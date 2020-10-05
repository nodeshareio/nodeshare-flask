from flask import jsonify, request, url_for
from backend.models import User
from backend.api import api
from backend.api.errors import bad_request
from backend import db
from backend.api.auth import token_auth
import json


@api.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@api.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@api.route('/users', methods=['POST'])
@token_auth.login_required
def create_user():
    data = json.loads(request.data) or {'error: no data'}
    if 'username' not in data \
        or 'email' not in data \
        or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@api.route('/users/delete',  methods=['POST'])
@token_auth.login_required
def delete_user():
    data = json.loads(request.data) or {'error: no data'}
    if 'username' not in data:
        return bad_request('please provide username')
    processed_data = (data["username"])
    user = User.query.filter_by(username=processed_data).first()
    db.session.delete(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response
   





