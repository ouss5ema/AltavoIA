from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from models.user import User
from models.session import Session
from models.password_reset import PasswordReset
from models.verification_code import VerificationCode
from utils.validators import (
    validate_email_format, validate_password_strength, 
    validate_username, mask_email, is_valid_email
)
from utils.token_utils import generate_token, generate_session_data
from utils.device_utils import generate_device_fingerprint
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Bad Request', 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirmPassword', '').strip()
        role = data.get('role', 1)
        
        # Validation de l'email
        is_valid, email_message = validate_email_format(email)
        if not is_valid:
            return jsonify({'message': email_message}), 400
        
        # Validation du nom d'utilisateur
        is_valid, username_message = validate_username(username)
        if not is_valid:
            return jsonify({'message': username_message}), 400
        
        # Validation du mot de passe
        is_valid, password_message = validate_password_strength(password)
        if not is_valid:
            return jsonify({'message': password_message}), 400
        
        # Vérification de la confirmation du mot de passe
        if not confirm_password:
            return jsonify({'message': 'Confirm Password is required'}), 400
        
        if password != confirm_password:
            return jsonify({'message': 'Passwords do not match'}), 400
        
        # Vérifier si l'email existe déjà
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'message': 'Please Try Again!'}), 400
        
        # Vérifier si le nom d'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message': 'Username already taken'}), 400
        
        # Créer le nouvel utilisateur
        new_user = User(
            email=email,
            username=username,
            password=password,  # Le hash est fait dans le constructeur
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'userId': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Error registering user'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '').strip()
        
        if not identifier or not password:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Identifier (username or email) and password are required.'
            }), 400
        
        # Chercher l'utilisateur par email ou username
        user = None
        if is_valid_email(identifier):
            user = User.query.filter_by(email=identifier, status=1).first()
        else:
            user = User.query.filter_by(username=identifier, status=1).first()
        
        # Vérifier l'utilisateur et le mot de passe
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid identifier or password.'
            }), 401
        
        # Générer le token et les données de session
        token_payload = {
            'sub': str(user.id),
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
        token = generate_token(token_payload)
        session_data = generate_session_data(request, token)
        
        # Vérifier s'il existe déjà une session active pour cet appareil
        existing_session = Session.query.filter_by(
            user_id=user.id,
            device_fingerprint=session_data['device_fingerprint'],
            status='active'
        ).first()
        
        if existing_session:
            # Mettre à jour la session existante
            existing_session.token = session_data['token']
            existing_session.device_name = session_data['device_name']
            existing_session.ip_address = session_data['ip_address']
            existing_session.user_agent = session_data['user_agent']
            existing_session.location = session_data['location']
            existing_session.last_accessed_at = datetime.datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': user.to_dict_safe(),
                'sessionId': existing_session.id,
                'sessionStatus': existing_session.status
            }), 200
        
        # Supprimer toute session en attente avec le même fingerprint
        Session.query.filter_by(
            user_id=user.id,
            device_fingerprint=session_data['device_fingerprint'],
            status='pending'
        ).delete()
        
        # Créer une nouvelle session en attente
        new_session = Session(
            user_id=user.id,
            status='pending',
            **session_data
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        masked_email = mask_email(user.email)
        
        return jsonify({
            'message': 'New device detected. Verification required.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': masked_email,
                'device_fingerprint': session_data['device_fingerprint'],
                'status': 'pending'
            }
        }), 202
        
    except Exception as e:
        db.session.rollback()
        print(f"Login error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not log in, try again later.'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Déconnexion d'un utilisateur"""
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        
        if not session_id:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Session ID is required'
            }), 400
        
        # Trouver et révoquer la session
        session = Session.query.filter_by(id=session_id).first()
        if session:
            session.revoke()
            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({
                'error': 'Not Found',
                'message': 'Session not found'
            }), 404
            
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not logout'
        }), 500

@auth_bp.route('/reset-password/initiate', methods=['POST'])
def initiate_reset_password():
    """Initier la réinitialisation du mot de passe"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Email is required'
            }), 400
        
        # Vérifier si l'email est valide
        is_valid, _ = validate_email_format(email)
        if not is_valid:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Chercher l'utilisateur
        user = User.query.filter_by(email=email, status=1).first()
        if not user:
            # Pour des raisons de sécurité, ne pas révéler si l'email existe
            return jsonify({'message': 'If the email exists, a reset link has been sent.'}), 200
        
        # Supprimer les anciens tokens de réinitialisation
        PasswordReset.query.filter_by(user_id=user.id).delete()
        
        # Créer un nouveau token de réinitialisation
        password_reset = PasswordReset(user_id=user.id)
        db.session.add(password_reset)
        db.session.commit()
        
        # Ici, vous pouvez envoyer l'email avec le token
        # Pour l'instant, on retourne le token (en production, envoyer par email)
        return jsonify({
            'message': 'If the email exists, a reset link has been sent.',
            'token': password_reset.token  # À supprimer en production
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Password reset initiation error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not initiate password reset'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Réinitialiser le mot de passe"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('newPassword', '').strip()
        confirm_password = data.get('confirmPassword', '').strip()
        
        if not token or not new_password or not confirm_password:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Token, new password, and confirm password are required'
            }), 400
        
        if new_password != confirm_password:
            return jsonify({'message': 'Passwords do not match'}), 400
        
        # Valider la force du nouveau mot de passe
        is_valid, password_message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'message': password_message}), 400
        
        # Chercher le token de réinitialisation
        password_reset = PasswordReset.query.filter_by(token=token).first()
        if not password_reset or not password_reset.is_valid():
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or expired reset token'
            }), 401
        
        # Mettre à jour le mot de passe
        user = User.query.get(password_reset.user_id)
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404
        
        user.password = user.hash_password(new_password)
        
        # Supprimer le token de réinitialisation
        db.session.delete(password_reset)
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Password reset error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not reset password'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtenir le profil de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'user': user.to_dict_safe()
        }), 200
        
    except Exception as e:
        print(f"Get profile error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not get profile'
        }), 500

@auth_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Obtenir toutes les sessions de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        sessions = Session.query.filter_by(
            user_id=current_user_id,
            status='active'
        ).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions]
        }), 200
        
    except Exception as e:
        print(f"Get sessions error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not get sessions'
        }), 500 