from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import os

db = SQLAlchemy()

def init_db(app):
    """Initialiser la base de données et créer la DB si elle n'existe pas"""
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    
    # Créer la base de données si elle n'existe pas
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Base de données '{engine.url.database}' créée avec succès!")
    
    db.init_app(app)
    
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        print("Tables créées avec succès!") 