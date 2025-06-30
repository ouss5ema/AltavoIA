from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.database import db
from flask_migrate import Migrate
from routes.auth_routes import auth_bp
from routes.verification_routes import verification_bp
from routes.conversation_routes import conversation_bp
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens n'expirent pas automatiquement
    
    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:@localhost/altavo_partners'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialiser les extensions
    CORS(app)
    JWTManager(app)
    db.init_app(app)
    Migrate(app, db)
    
    # Enregistrer uniquement les blueprints d'authentification
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(verification_bp, url_prefix='/api/verification')
    app.register_blueprint(conversation_bp, url_prefix='/api/conversations')
    
    # Route de test
    @app.route('/')
    def home():
        return {'message': 'Altavo Partners API - Python Version', 'status': 'running'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'database': 'connected'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 