from config.database import db
from datetime import datetime, timedelta
import secrets
import string

class PasswordReset(db.Model):
    __tablename__ = 'reset_password'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, expires_at=None):
        self.user_id = user_id
        self.token = self.generate_token()
        self.expires_at = expires_at or (datetime.utcnow() + timedelta(hours=1))
    
    def generate_token(self, length=32):
        """Générer un token sécurisé"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def is_expired(self):
        """Vérifier si le token a expiré"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Vérifier si le token est valide"""
        return not self.is_expired()
    
    def to_dict(self):
        """Convertir l'objet en dictionnaire"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid()
        }
    
    def __repr__(self):
        return f'<PasswordReset {self.id} - User {self.user_id}>' 