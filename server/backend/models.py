from datetime import datetime, timedelta, date
from hashlib import md5
from flask import jsonify, url_for
from time import time
from flask_login import UserMixin
from passlib.hash import sha256_crypt
import jwt
from backend import db, login, app
import base64
import os
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm.collections import attribute_mapped_collection




class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {'items': [item.to_dict() for item in resources.items],
                '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': resources.pages,
            'total_items': resources.total
        },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
            'next': url_for(endpoint, page=page + 1, per_page=per_page,
                            **kwargs) if resources.has_next else None,
            'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                            **kwargs) if resources.has_prev else None
        }
        }
        return data

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# likes = db.Table(
#     'likes',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('node_id', db.Integer, db.ForeignKey('node.id'))
# )

class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    info = db.Column(db.String(1000))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary='user_roles')
    comments = db.relationship('Comment', foreign_keys='Comment.author_id', backref='author', lazy='dynamic')
    nodes = db.relationship('Node', backref='creator', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')


    def __repr__(self):
        return f'{self.username}'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0            
 
    def followed_nodes(self):
        followed = Node.query.join(
            followers, (followers.c.followed_id == Node.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Node.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Node.timestamp.desc()) 

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }

        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):

        for field in ['username', 'email', 'info']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def set_password(self, password):
        self.password_hash = sha256_crypt.encrypt(password)

    def check_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

    def get_token(self, expires_in=86400):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def get_reset_password_token(self, expires_in=1200):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.secret_key, algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.secret_key, algorithms=[
                            'HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def get_new_user_token(email, expires_in=604800):
        return jwt.encode({'new_user': email, 'exp': time() + expires_in}, app.secret_key, algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_secure_register_token(token):
        try:
            id = jwt.decode(token, app.secret_key, algorithms=[
                            'HS256'])['new_user']
            return True
        except:
            return False
        

    def get_roles(self):
            return str(self.roles)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class OAuth(OAuthConsumerMixin, db.Model):
    __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
    provider_user_id = db.Column(db.String(256), nullable=False)
    provider_user_login = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User,backref=db.backref("oauth", collection_class=attribute_mapped_collection("provider"),
            cascade="all, delete-orphan"))


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return (self.name)

# Association table - does this need to be a model?  No...
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    def __repr__(self):
        return f'{self.author_id=} \n{self.node_id=} \n{self.body=}'


class Node(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=False)
    description = db.Column(db.String(250), unique=False)
    data = db.Column(db.Text(), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    premium = db.Column(db.Boolean, unique=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comments = db.relationship('Comment', foreign_keys='Comment.node_id', backref='node', lazy='dynamic')
    approved = db.Column(db.Boolean, unique=False, default=False)
    sample_path = db.Column(db.String(250), unique=False)



    def __repr__(self):
        return f'Node ID: {self.id} \nTitle: {self.title} \nDescription: {self.description}'

    def to_dict(self, include_email=True):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp,
            'user_id': self.userid,
        }
        return data

    def from_dict(self, data, approved=False):
        data['data'] = data['ns_string']
        data['approved'] = approved
        for field in ['title', 'description', 'data', 'approved']:
            if field in data:
                setattr(self, field, data[field])



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))