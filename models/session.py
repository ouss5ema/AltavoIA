from config.database import db
from datetime import datetime, timedelta
import uuid

class Session(db.Model):
    __tablename__ = 'users_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.Enum('active', 'expired', 'revoked', 'pending', name='session_status'), 
                      default='active', nullable=False)
    token = db.Column(db.Text, nullable=False)
    device_fingerprint = db.Column(db.String(255), nullable=False, index=True)
    device_name = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=False, default='127.0.0.1')
    user_agent = db.Column(db.Text, nullable=False, default='unknown')
    location = db.Column(db.String(255), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    
    def __init__(self, user_id, token, device_fingerprint, device_name=None, 
                 ip_address='127.0.0.1', user_agent='unknown', location=None, 
                 expires_at=None, status='active'):
        self.user_id = user_id
        self.token = token
        self.device_fingerprint = device_fingerprint
        self.device_name = device_name
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.location = location
        self.status = status
        self.expires_at = expires_at or (datetime.utcnow() + timedelta(days=30))
        self.last_accessed_at = datetime.utcnow()
    
    def is_expired(self):
        """Vérifier si la session a expiré"""
        return datetime.utcnow() > self.expires_at
    
    def is_active(self):
        """Vérifier si la session est active"""
        return self.status == 'active' and not self.is_expired()
    
    def update_last_accessed(self):
        """Mettre à jour le timestamp de dernière accès"""
        self.last_accessed_at = datetime.utcnow()
        db.session.commit()
    
    def revoke(self):
        """Révoquer la session"""
        self.status = 'revoked'
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convertir l'objet en dictionnaire"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'device_fingerprint': self.device_fingerprint,
            'device_name': self.device_name,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'location': self.location,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Session {self.id} - User {self.user_id}>' 