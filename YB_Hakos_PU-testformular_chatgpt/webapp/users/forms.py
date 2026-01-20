from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flask_login import current_user
from webapp.model.db import User
from sqlalchemy import func


class RegistrationForm(FlaskForm):
    username = StringField('Benutzername',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    firstname = StringField('Vorname',validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Nachname',validators=[DataRequired(), Length(min=2, max=20)])
    vds_number = IntegerField('VDS Mitgliedsnummer')
    password = PasswordField('Passwort', validators=[DataRequired()])
    confirm_password = PasswordField('Passwort wiederholen',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email oder Benutzername',
                        validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember = BooleanField('An mich erinnern')
    submit = SubmitField('Anmelden')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('First Name')
    surname = StringField('Surname')
    vds_number = IntegerField('VDS Mitgliedsnummer')
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.name:
#            user = User.query.filter_by(name=username.data).first()
            user = User.query.filter(
                func.upper(User.name) == username.data.upper()
            ).first()

            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
#            user = User.query.filter_by(email=email.data).first()
            user = User.query.filter(
                func.upper(User.email) == email.data.upper()
            ).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
#        user = User.query.filter_by(email=email.data).first()
        user = User.query.filter(
            func.upper(User.email) == email.data.upper()
        ).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
