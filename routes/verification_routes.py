from flask import Blueprint, request, jsonify
from config.database import db
from models.user import User
from models.session import Session
from models.verification_code import VerificationCode
import datetime

verification_bp = Blueprint('verification', __name__)

MAX_ATTEMPTS = 5

@verification_bp.route('/verify-device', methods=['POST'])
def verify_device():
    """Vérifier un appareil avec un code de vérification"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        user_id = data.get('userId')
        fingerprint = data.get('fingerprint')
        code = data.get('code')
        
        if not user_id or not fingerprint or not code:
            return jsonify({
                'error': 'Bad Request',
                'message': 'User ID, fingerprint, and code are required.'
            }), 400
        
        # Chercher l'enregistrement de vérification
        verification_record = VerificationCode.query.filter_by(
            user_id=user_id,
            device_fingerprint=fingerprint
        ).first()
        
        if not verification_record:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or expired verification code.'
            }), 401
        
        # Vérifier le nombre de tentatives
        if verification_record.attempts >= MAX_ATTEMPTS:
            # Supprimer le code de vérification et la session
            db.session.delete(verification_record)
            Session.query.filter_by(
                user_id=user_id,
                device_fingerprint=fingerprint,
                status='pending'
            ).delete()
            db.session.commit()
            
            return jsonify({
                'error': 'Too Many Requests',
                'message': 'Too many verification attempts.'
            }), 429
        
        # Vérifier si le code est correct et non expiré
        is_code_correct = verification_record.code == code
        is_code_expired = verification_record.is_expired()
        
        if not is_code_correct or is_code_expired:
            verification_record.increment_attempts()
            
            if verification_record.attempts >= MAX_ATTEMPTS:
                # Supprimer le code de vérification et la session
                db.session.delete(verification_record)
                Session.query.filter_by(
                    user_id=user_id,
                    device_fingerprint=fingerprint,
                    status='pending'
                ).delete()
                db.session.commit()
                
                return jsonify({
                    'error': 'Too Many Requests',
                    'message': 'Too many attempts. The device has been blacklisted.'
                }), 429
            
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or expired verification code.'
            }), 400
        
        # Chercher la session en attente
        session = Session.query.filter_by(
            user_id=user_id,
            device_fingerprint=fingerprint,
            status='pending'
        ).first()
        
        if not session:
            db.session.delete(verification_record)
            db.session.commit()
            return jsonify({
                'error': 'Unauthorized',
                'message': 'No pending session found or session already verified.'
            }), 401
        
        # Activer la session
        session.status = 'active'
        session.last_accessed_at = datetime.datetime.utcnow()
        
        # Supprimer le code de vérification
        db.session.delete(verification_record)
        db.session.commit()
        
        # Récupérer les informations de l'utilisateur
        user = User.query.get(user_id)
        
        return jsonify({
            'message': 'Device verified and session activated',
            'token': session.token,
            'user': user.to_dict_safe(),
            'sessionId': session.id,
            'sessionStatus': session.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Verify device error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not verify device. Please try again later.'
        }), 500

@verification_bp.route('/resend-code', methods=['POST'])
def resend_verification_code():
    """Renvoyer un code de vérification"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        user_id = data.get('userId')
        fingerprint = data.get('fingerprint')
        
        if not user_id or not fingerprint:
            return jsonify({
                'error': 'Bad Request',
                'message': 'User ID and fingerprint are required.'
            }), 400
        
        # Vérifier s'il existe une session en attente
        session = Session.query.filter_by(
            user_id=user_id,
            device_fingerprint=fingerprint,
            status='pending'
        ).first()
        
        if not session:
            return jsonify({
                'error': 'Not Found',
                'message': 'No pending session found.'
            }), 404
        
        # Supprimer l'ancien code de vérification
        VerificationCode.query.filter_by(
            user_id=user_id,
            device_fingerprint=fingerprint
        ).delete()
        
        # Créer un nouveau code de vérification
        verification_code = VerificationCode(
            user_id=user_id,
            device_fingerprint=fingerprint
        )
        
        db.session.add(verification_code)
        db.session.commit()
        
        # Ici, vous pouvez envoyer l'email avec le nouveau code
        # Pour l'instant, on retourne le code (en production, envoyer par email)
        return jsonify({
            'message': 'Verification code resent successfully.',
            'code': verification_code.code  # À supprimer en production
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Resend code error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not resend verification code.'
        }), 500

@verification_bp.route('/check-status', methods=['POST'])
def check_verification_status():
    """Vérifier le statut de vérification d'un appareil"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        user_id = data.get('userId')
        fingerprint = data.get('fingerprint')
        
        if not user_id or not fingerprint:
            return jsonify({
                'error': 'Bad Request',
                'message': 'User ID and fingerprint are required.'
            }), 400
        
        # Vérifier s'il existe une session active
        active_session = Session.query.filter_by(
            user_id=user_id,
            device_fingerprint=fingerprint,
            status='active'
        ).first()
        
        if active_session:
            return jsonify({
                'status': 'active',
                'sessionId': active_session.id,
                'message': 'Device is already verified and active.'
            }), 200
        
        # Vérifier s'il existe une session en attente
        pending_session = Session.query.filter_by(
            user_id=user_id,
            device_fingerprint=fingerprint,
            status='pending'
        ).first()
        
        if pending_session:
            # Vérifier s'il existe un code de vérification
            verification_code = VerificationCode.query.filter_by(
                user_id=user_id,
                device_fingerprint=fingerprint
            ).first()
            
            if verification_code and verification_code.is_valid():
                return jsonify({
                    'status': 'pending',
                    'message': 'Device verification is pending.',
                    'hasCode': True
                }), 200
            else:
                return jsonify({
                    'status': 'pending',
                    'message': 'Device verification is pending but no valid code found.',
                    'hasCode': False
                }), 200
        
        return jsonify({
            'status': 'not_found',
            'message': 'No session found for this device.'
        }), 404
        
    except Exception as e:
        print(f"Check status error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not check verification status.'
        }), 500 