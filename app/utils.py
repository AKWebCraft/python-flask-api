import jwt
from flask import request, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta  # <-- Add missing imports
from .models import User
from .blacklist import token_blacklist  # Import the blacklist

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # Check if the token is blacklisted
        if token in token_blacklist:
            return jsonify({'message': 'Token has been revoked!'}), 401

        try:
            secret_key = current_app.config['SECRET_KEY']
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def generate_token(user_id):
    """
    Generate a JWT token for the user.
    """
    secret_key = current_app.config['SECRET_KEY']
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {
            'user_id': user_id,
            'exp': expiration_time
        },
        secret_key,
        algorithm="HS256"
    )
    return token



# import jwt
# from flask import request, jsonify, current_app
# from functools import wraps
# from datetime import datetime, timedelta
# from .models import User

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('x-access-token')
#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 401
#         try:
#             # Access SECRET_KEY using current_app
#             secret_key = current_app.config['SECRET_KEY']
#             data = jwt.decode(token, secret_key, algorithms=["HS256"])
#             current_user = User.query.filter_by(id=data['user_id']).first()
#         except jwt.ExpiredSignatureError:
#             return jsonify({'message': 'Token has expired!'}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({'message': 'Token is invalid!'}), 401
#         return f(current_user, *args, **kwargs)
#     return decorated

# def generate_token(user_id):
#     """
#     Generate a JWT token for the user.
#     """
#     secret_key = current_app.config['SECRET_KEY']  # Use current_app to access the app config
#     token = jwt.encode(
#         {
#             'user_id': user_id,
#             'exp': datetime.utcnow() + timedelta(hours=1)
#         },
#         secret_key,
#         algorithm="HS256"
#     )
#     return token

