from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..utils import generate_token
from datetime import datetime
from ..blacklist import token_blacklist
from ..utils import token_required
from .. import db

auth_bp = Blueprint('auth', __name__)

#REGISTETR 
@auth_bp.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required!'}), 400

    username = data['username'].strip()
    password = data['password'].strip()

    if not username or not password:
        return jsonify({'message': 'Username and password cannot be empty!'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long!'}), 400

    if len(username) < 3:
        return jsonify({'message': 'Username must be at least 3 characters long!'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists!'}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    token = generate_token(new_user.id)

    return jsonify({
        'message': 'User registered successfully!',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'password_hash': new_user.password, 
        },
        'token': token
    }), 201

#LOGIN 
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required!'}), 400

    username = data['username'].strip()
    password = data['password'].strip()

    if not username or not password:
        return jsonify({'message': 'Username and password cannot be empty!'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password!'}), 401

    token = generate_token(user.id)

    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Login successful!',
        'user': {
            'id': user.id,
            'username': user.username,
            'last_login': user.last_login
        },
        'token': token
    }), 200

#LOGOUT
@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = request.headers.get('x-access-token')

    token_blacklist.add(token)

    return jsonify({'message': 'Logged out successfully!'}), 200