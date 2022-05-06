from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_409_CONFLICT
from flask import Blueprint, app, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flasgger import swag_from
from src.database import User, db
from flask_login import LoginManager, login_user

from time import sleep

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth", template_folder='template')
LoginManager.login_view = 'login'


# @swag_from('./docs/auth/register.yaml')
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        email = userDetails['email']
        password = userDetails['password']

        if len(password) < 6:
            return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

        if len(username) < 3:
            return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

        if not username.isalnum() or " " in username:
            return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

        if not validators.email(email):
            return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

        if User.query.filter_by(email=email).first() is not None:
            return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

        if User.query.filter_by(username=username).first() is not None:
            return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

        pwd_hash = generate_password_hash(password)

        user = User(username=username, password=pwd_hash, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')


# @swag_from('./docs/auth/login.yaml')
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # email = request.json.get('email', '')
        # password = request.json.get('password', '')
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']

        user = User.query.filter_by(username=username).first()

        if user:
            is_pass_correct = check_password_hash(user.password, password)
            if is_pass_correct:
                refresh = create_refresh_token(identity=user.id)
                access = create_access_token(identity=user.id)
                login_user(user)
                # resp_header = {'Authorization': 'Bearer {}'.format(access)}
                resp = redirect(url_for('public_1.handle_public_1'), code=302)
                return resp
        else:
            flash('用户名或密码不正确')
            redirect(url_for('auth.login'))
    return render_template('login.html')
    # jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
# @jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'username': user.username,
        'email': user.email
    }), HTTP_200_OK
