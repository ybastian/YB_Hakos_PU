from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlparse
from webapp import bcrypt, db
from webapp.model.db import User, Post
from webapp.users import users
from webapp.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from webapp.users.utils import save_picture, send_reset_email
from sqlalchemy import func


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(name=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    firstname=form.firstname.data,
                    surname=form.surname.data,
                    vds_number=form.vds_number.data,
                    role='Gast',
                    approved=False
                    )
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Es ist ein Fehler aufgetreten: {e}. Bitte melden Sie sich beim Systemadministrator.', 'error')

        flash('Ihr Benutzer ist registriert! Sie können sich jetzt anmelden', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(    # zuerst schauen, ob eine email Adresse eingegeben wurde
            func.upper(User.email) == form.email.data.upper()
        ).first()

        if not user:   # wenn das nichts bringt, annehmen, dass der Username im Feld steht
           user = User.query.filter(
                func.upper(User.name) == form.email.data.upper()
            ).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next', '').replace('\\', '')  # Remove backslashes
            if not urlparse(next_page).netloc and not urlparse(next_page).scheme: # allow only relative path
                # relative path, safe to redirect (no protocol and no hostname in url)
                return redirect(next_page)
            # Default to the home page if the next_page is invalid or unsafe
            return redirect(url_for('main.home'))
        else:
            flash('Login nicht erfolgreich. Bitte prüfen Sie ihre Angaben!', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.username.data
        current_user.email = form.email.data
        current_user.firstname = form.firstname.data
        current_user.surname = form.surname.data
        current_user.vds_number = form.vds_number.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.name
        form.email.data = current_user.email
        form.firstname.data = current_user.firstname
        form.surname.data = current_user.surname
        form.vds_number.data = current_user.vds_number
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(name=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
