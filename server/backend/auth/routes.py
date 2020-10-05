from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from backend import db, app, role_required
from backend.auth import auth
from backend.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm, RegistrationForm, NewUserRequestForm
from backend.models import User, UserRoles
from backend.auth.email import send_password_reset_email, send_new_user_request_email


''' INTERNAL  BLUEPRINT '''


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User has been registered and can log in', 'success')
        return redirect(url_for('site.index'))
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('site.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'warning')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('site.index')
        user.logged_in=True
        db.session.commit()
        flash('You are now logged in', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


# Logout
@auth.route('/logout')
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('site.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('site.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('donate'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/newuserrequest', methods=['GET', 'POST'])
@role_required("ADMIN")
def new_user_request():
    '''
    For Admin  to send secure registration request email to potential user
    '''
    form = NewUserRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        send_new_user_request_email(email)
        flash('Email sent for New User Request', 'success')
        return redirect(url_for('admin.index'))
    return render_template('auth/send_new_user_request.html', title='Request New User', form=form)


@auth.route('/secureregister/<token>', methods=['GET', 'POST'])
def secure_register(token):
    if current_user.is_authenticated:
        return redirect(url_for('site.index'))
    admin = User.query.get(1)
    form = RegistrationForm()
    if User.verify_secure_register_token(token):
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration Complete', 'success')
            return redirect(url_for('site.index'))
    return render_template('auth/register.html', title='Register', form=form)

