from flask import render_template
from backend import app, mail
from backend.email import send_email
from backend.models import User

''' INTERNAL SUBDOMAIN BLUEPRINT '''

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password', sender=app.config['ADMINS'], recipients=[user.email], text_body=render_template(
        'email/reset_password.txt', user=user, token=token), html_body=render_template('email/reset_password.html', user=user, token=token))


def send_new_user_request_email(email):
    token = User.get_new_user_token(email)
    print(f"{token=}")
    send_email('Register for NodeShare.io', sender=app.config['ADMINS'], recipients=[email], text_body=render_template(
        'email/new_user.txt', email=email, token=token), html_body=render_template('email/new_user.html', email=email, token=token))
