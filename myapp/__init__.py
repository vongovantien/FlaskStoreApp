from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_mail import Mail, Message
import cloudinary
from authlib.integrations.flask_client import OAuth

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

app.config["GOOGLE_CLIENT_ID"] = '811591875550-t8c97gln5ej8k2q7po2qnr576g3mmkms.apps.googleusercontent.com'
app.config["GOOGLE_CLIENT_SECRET"] = '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'
app.config["GITHUB_CLIENT_ID"] = '2daf9689e45e70ca3931'
app.config["GITHUB_CLIENT_SECRET"] = 'c6d06bdf045792cb0165f3d6a27b824e159a928f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/saledb'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = 'hifgsdfgahrt5àygsffhj6jj45YTẺTGHMKẠtrtfDFG'
app.config['PAGE_SIZE'] = 5
app.config['COMMENT_SIZE'] = 4
app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'vongovantien@gmail.com'
app.config['MAIL_PASSWORD'] = 'vongovantien30820'
app.config['MAIL_DEFAULT_SENDER'] = 'vongovantien@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)
login = LoginManager(app=app)
oauth = OAuth(app)
db = SQLAlchemy(app=app)
migrate = Migrate(app, db)

google = oauth.register(
    name='google',
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)
github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

cloudinary.config(
    cloud_name='dgct8zpvp',
    api_key='631943736442228',
    api_secret='4xKADk_UWqAKS7vlOl8qst_LUjw'
)
