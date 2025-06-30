import uuid
from config.database import db
from datetime import datetime, timedelta
import secrets
import string

class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    device_fingerprint = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)  # Code à 6 chiffres
    attempts = db.Column(db.Integer, default=0, nullable=False)
    resend_attempts = db.Column(db.Integer, default=0, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, device_fingerprint, expires_at=None):
        self.user_id = user_id
        self.device_fingerprint = device_fingerprint
        self.code = self.generate_code()
        self.expires_at = expires_at or (datetime.utcnow() + timedelta(minutes=10))
    
    def generate_code(self, length=6):
        """Générer un code numérique à 6 chiffres"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    def is_expired(self):
        """Vérifier si le code a expiré"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Vérifier si le code est valide"""
        return not self.is_expired() and self.attempts < 5
    
    def increment_attempts(self):
        """Incrémenter le nombre de tentatives"""
        self.attempts += 1
        db.session.commit()
    
    def increment_resend_attempts(self):
        """Incrémenter le nombre de tentatives de renvoi"""
        self.resend_attempts += 1
        db.session.commit()
    
    def check_code(self, code):
        """Vérifier si le code fourni est correct"""
        if self.is_expired():
            return False
        if self.attempts >= 5:
            return False
        return self.code == code
    
    def to_dict(self):
        """Convertir l'objet en dictionnaire"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_fingerprint': self.device_fingerprint,
            'code': self.code,  # Attention: ne pas exposer en production
            'attempts': self.attempts,
            'resend_attempts': self.resend_attempts,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid()
        }
    
    def __repr__(self):
        return f'<VerificationCode {self.id} - User {self.user_id}>' 