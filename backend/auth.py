import re
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from .models import db, User, AuditLog
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()
SECRET_KEY = os.environ.get('SECRET_KEY', 'vota-ciudadano-super-secret-key')

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    if not validate_password(password):
        return jsonify({'error': 'Password must be 8+ chars, with upper, lower and numbers'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password_hash=hashed_pw)
    
    db.session.add(new_user)
    db.session.commit()

    # Log action
    log = AuditLog(action='USER_REGISTER', user_id=new_user.id, details=f'Registered: {email}', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'is_admin': user.is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')

        log = AuditLog(action='USER_LOGIN', user_id=user.id, details='User logged in', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()

        return jsonify({'token': token, 'user': {'email': user.email, 'is_admin': user.is_admin}})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/me', methods=['DELETE'])
def delete_account():
    # Token verification would be handled by a decorator in a real app
    # For simplicity, we'll extract it here or use a helper
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Token missing'}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = User.query.get(user_id)
        
        if user:
            # Audit log before deletion
            log = AuditLog(action='USER_DELETE', user_id=user_id, details=f'User {user.email} deleted account', ip_address=request.remote_addr)
            db.session.add(log)
            
            # Delete related data or anonymize? Requirement says permanent deletion.
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Account deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401

    return jsonify({'error': 'User not found'}), 404
