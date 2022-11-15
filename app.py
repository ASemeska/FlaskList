import os
from flask import Flask, render_template, redirect, url_for, jsonify, make_response, request
from flask_login import LoginManager,UserMixin,login_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from wtforms import StringField,PasswordField,SubmitField,IntegerField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo
import requests
import json
import sqlite3



basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SECRET_KEY'] = '152asdqwe488ewr327159a'
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#++++++++++++++++CLASES++++++++++++++++#
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Message(db.Model):
     __tablename__ = "message"
     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     title = db.Column(db.String(50), unique=True, nullable=False)
     message = db.Column(db.String(500), unique=True, nullable=False)
     category = db.Column(db.String(500), unique=True, nullable=False)


@login_manager.user_loader
def load_user(user_email):
    return User.query.get(int(user_email))

#++++++++++++++++FORMS+++++++++++++++++#
class RegisterForm(FlaskForm):
    username = StringField('Username', [DataRequired()])
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    approved_password = PasswordField("Repeat password", [EqualTo('password', "Passwords needs to match")])
    submit = SubmitField('Register')


    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Log In')

class MessageForm(FlaskForm):
    title = StringField('Title', [DataRequired()])
    message = StringField('Message', [DataRequired()])
    category = StringField('Category', [DataRequired()])
    submit = SubmitField('Submit message')


#++++++++++++++++ROUTES++++++++++++++++#
@app.route("/", methods=['GET', 'POST'], endpoint = 'my_login')
def home():
    form = LoginForm() 
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
               login_user(user)
               return redirect(url_for('user'))
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm() 
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email= form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('my_login'))
    return render_template('register.html', form=form)


@app.route("/user", methods=['GET', 'POST'])
def user():
    form = MessageForm()
    if form.validate_on_submit():
            new_message = Message(title = form.title.data, message = form.message.data, category = form.category.data)
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('user'))
    return render_template("user.html", form = form)


if __name__ == "__main__":
    app.run(debug=True)
