from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, logout_user, login_required
from loguru import logger

from memento import db, bcrypt
from memento.users.forms import *
from memento.users.utils import save_picture, default_lifeline

user_bp = Blueprint('user_bp', __name__, static_folder='static', template_folder='templates')


@user_bp.route("/registration", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, birthdate=form.date_of_birth.data)
        logger.info('Adding new user to the database with the username: {}, email: {}'.format(user.username, user.email))
        ### TODO: flush/commit everything in one call
        db.session.add(user)
        logger.info('Flushing user to the database')
        db.session.flush()
        lifeline = default_lifeline(user)
        logger.info("Flushing user's {} lifelines to the database".format(user.username))
        db.session.add(lifeline)
        db.session.commit()
        logger.info('Account has been successfully created!')
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('user_bp.login'))
    return render_template('registration.html', title='Register', form=form)


@user_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('matrix_bp.matrix'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            session['username'] = user.username
            next_page = request.args.get('next')
            logger.info('Login successfull for the user entry with username: {}.'.format(user.username))
            # flash('Login Successfull! This is the layout of your life!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('matrix_bp.matrix'))
        else:
            logger.info('Login Unsuccessful for the user entry with username: {}'.format(user.username))
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@user_bp.route("/logout")
@login_required
def logout():
    logger.info('User {} has logged out'.format(current_user.username))
    logout_user()
    return redirect(url_for('home_bp.home'))

@user_bp.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.date_of_birth = form.date_of_birth.data
        logger.info('Committing to database updated user data')
        db.session.commit()
        logger.info('Account info sussefully updated for the user: {}.'.format(current_user.username))
        flash('Your account has been updated!', 'success')
        return redirect(url_for('user_bp.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
