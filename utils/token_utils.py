import jwt
import datetime
import os
from flask import current_app

def generate_token(payload, expires_in=None):
    """Générer un token JWT"""
    if expires_in is None:
        expires_in = datetime.timedelta(days=30)
    
    payload['exp'] = datetime.datetime.utcnow() + expires_in
    payload['iat'] = datetime.datetime.utcnow()
    
    secret_key = current_app.config.get('JWT_SECRET_KEY', 'default-secret-key')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token):
    """Vérifier un token JWT"""
    try:
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"
    except Exception as e:
        return False, str(e)

def decode_token(token):
    """Décoder un token JWT sans vérification (pour debug)"""
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        return None

def generate_session_data(request, token):
    """Générer les données de session"""
    from utils.device_utils import generate_device_fingerprint, get_device_name
    
    device_fingerprint = generate_device_fingerprint(request)
    device_name = get_device_name(request)
    ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '127.0.0.1')
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    return {
        'token': token,
        'device_fingerprint': device_fingerprint,
        'device_name': device_name,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'location': None  # Peut être implémenté avec un service de géolocalisation
    } 