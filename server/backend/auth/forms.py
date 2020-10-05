from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from backend.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Display Name', [validators.DataRequired()])
    email = StringField(
        'Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    confirm = PasswordField('Confirm Password', [validators.DataRequired(
    ), validators.EqualTo('password', message='Passwords do not match')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise validators.ValidationError(
                'Please choose a different username.', 'warning')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise validators.ValidationError(
                'Email in use, please use a different email.', 'warning')


# LOGIN FORM CLASS
class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# FORGOT PASSWORD FORM CLASS
class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        'Email', [validators.DataRequired(), validators.Email()])
    submit = SubmitField('Request Password Reset')


# RESET PASSWORD FORM
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', [validators.DataRequired()])
    password2 = PasswordField('Repeat Password', [validators.DataRequired(), validators.EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class NewUserRequestForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    submit = SubmitField('Send New User Request')