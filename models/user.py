import bcrypt
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime
from config.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from .conversation import Conversation
from .document import Document

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    username = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Integer, default=1, nullable=False)  # 0=admin, 1=user
    status = db.Column(db.Integer, default=1, nullable=False)  # 1=active, 0=inactive
    user_groups = db.Column(JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')
    password_resets = db.relationship('PasswordReset', backref='user', lazy=True, cascade='all, delete-orphan')
    verification_codes = db.relationship('VerificationCode', backref='user', lazy=True, cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', back_populates='user', lazy=True, cascade="all, delete-orphan")
    documents = db.relationship('Document', back_populates='user', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, email, username, password, role=1, status=1, user_groups=None):
        self.email = email
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        self.status = status
        self.user_groups = user_groups
    
    def hash_password(self, password):
        """Hasher le mot de passe avec bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Vérifier le mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self):
        """Convertir l'objet en dictionnaire"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'status': self.status,
            'user_groups': self.user_groups,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_safe(self):
        """Convertir l'objet en dictionnaire sans informations sensibles"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password) 