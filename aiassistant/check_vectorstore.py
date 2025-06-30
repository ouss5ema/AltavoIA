import os
import sys
sys.path.append('..')

from rag_api import get_user_vectorstore, CHROMA_DB_PATH, SessionLocal, embedding_model
from models.user import User
from langchain_community.vectorstores import Chroma

def check_user_vectorstore(user_id: int):
    """Vérifie le contenu de la base vectorielle pour un utilisateur"""
    
    print(f"=== Vérification de la base vectorielle pour l'utilisateur {user_id} ===")
    
    # Connexion à la base de données
    db = SessionLocal()
    
    try:
        # Récupérer l'utilisateur
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"Utilisateur {user_id} non trouvé")
            return
        
        print(f"Utilisateur: {user.username}")
        
        # Vérifier si la collection existe
        collection_name = f"user_{user_id}_collection"
        print(f"Collection: {collection_name}")
        
        # Essayer de charger la base vectorielle
        try:
            vectorstore = Chroma(
                persist_directory=CHROMA_DB_PATH,
                collection_name=collection_name,
                embedding_function=embedding_model
            )
            
            # Compter les documents
            collection = vectorstore._collection
            count = collection.count()
            print(f"Nombre de documents dans la collection: {count}")
            
            if count > 0:
                # Essayer une recherche simple
                print("\n--- Test de recherche ---")
                results = vectorstore.similarity_search("JavaScript", k=3)
                print(f"Résultats pour 'JavaScript': {len(results)} documents")
                
                for i, doc in enumerate(results):
                    print(f"\n--- Document {i+1} ---")
                    print(doc.page_content[:300])
                    print("---")
                    
                # Essayer avec scores
                print("\n--- Test avec scores ---")
                try:
                    docs_and_scores = vectorstore.similarity_search_with_score("JavaScript", k=3)
                    for i, (doc, score) in enumerate(docs_and_scores):
                        print(f"Document {i+1} - Score: {score:.4f}")
                        print(doc.page_content[:200])
                        print("---")
                except Exception as e:
                    print(f"Erreur avec scores: {e}")
            else:
                print("❌ Aucun document dans la collection")
                
        except Exception as e:
            print(f"❌ Erreur lors du chargement de la base vectorielle: {e}")
            
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user_vectorstore(1) 