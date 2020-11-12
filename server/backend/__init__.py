
from flask import Flask, redirect, url_for, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_manager
from flask_login.mixins import AnonymousUserMixin 
from flask_migrate import Migrate
from flask_mail import Mail
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
from flask_cors import CORS
from functools import wraps
from flask_socketio import SocketIO
import os
from os.path import abspath, join, dirname
from dotenv import load_dotenv
import eventlet
from flask import Flask
from flask_mqtt import Mqtt

'''
DEV ONLY - disable in production!!!!!!
'''

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


'''
UTILS
'''

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
basedir = os.path.abspath(os.path.dirname(__file__))

'''
APP
'''
app = Flask(__name__) 

# Custom static data
@app.route('/cdn/<path:filename>')
def preview(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
'''
APP CONFIGURATION
'''
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['DEBUG'] = True
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASS')
app.secret_key =  os.environ.get('SECRET_KEY')
app.config['MQTT_BROKER_URL'] = os.environ.get('MQTT_BROKER_URL')
app.config['MQTT_BROKER_PORT'] = int(os.environ.get('MQTT_BROKER_PORT'))
app.config['MQTT_USERNAME'] = os.environ.get('MQTT_USERNAME')
app.config['MQTT_PASSWORD'] = os.environ.get('MQTT_PASSWORD')
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/media/')
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")


'''
INSTANTIATE PLUGINS
'''
mqtt = Mqtt(app)
mqtt.client.tls_set()
cors = CORS(app, resources={r"/*": {"origins": "*"}})
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# limiter = Limiter(
#     app,
#     key_func=get_remote_address,
#     default_limits=["5000 per day", "2000 per hour"],
# )

'''
SOCKET-IO

'''
socketio = SocketIO() 
socketio.init_app(app, message_queue='redis://', async_mode = 'eventlet')




''' 
LOGIN MANAGER 
'''
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        pass
    @staticmethod
    def get_roles():
        return [False]

login = LoginManager(app)
login.login_view = 'auth.login'
login.login_message_category = "warning"
login.anonymous_user = Anonymous
''' 
DEFINE CUSTOM DECORATORS 
'''

def role_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return login.unauthorized()
            urole = current_user.get_roles()
            if ( ( role not in urole) and (role != "ANY")):
                flash("Unauthorized user role for this operation", 'danger')
                return redirect(request.referrer)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

'''
TEMPLATE FILTERS
'''
@app.template_filter('extension')
def ext_filter(s):
    return s.split('.')[-1]

'''
IMPORT BLUEPRINTS
'''

from backend.site import site 
from backend.api import api 
from backend.admin import admin
from backend.auth import auth 
from backend.errors import err 
from backend.oauth import google_blueprint

'''
REGISTER BLUEPRINTS
'''

app.register_blueprint(site)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(err, url_prefix='/error')
app.register_blueprint(google_blueprint, url_prefix="/login")
