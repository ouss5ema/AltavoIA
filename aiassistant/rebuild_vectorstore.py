import os
import sys
sys.path.append('..')

from rag_api import get_user_vectorstore, embedding_model, CHROMA_DB_PATH, SessionLocal
from models.user import User
from models.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma

def rebuild_user_vectorstore(user_id: int):
    """Reconstruit la base vectorielle pour un utilisateur donné"""
    
    # Connexion à la base de données
    db = SessionLocal()
    
    try:
        # Récupérer l'utilisateur
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"Utilisateur {user_id} non trouvé")
            return
        
        print(f"Reconstruction de la base vectorielle pour l'utilisateur {user.username} (ID: {user_id})")
        
        # Supprimer l'ancienne collection si elle existe
        try:
            old_vectorstore = Chroma(
                persist_directory=CHROMA_DB_PATH,
                collection_name=f"user_{user_id}_collection",
                embedding_function=embedding_model
            )
            old_vectorstore.delete_collection()
            print("Ancienne collection supprimée")
        except:
            print("Aucune ancienne collection à supprimer")
        
        # Créer une nouvelle collection
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            collection_name=f"user_{user_id}_collection",
            embedding_function=embedding_model
        )
        
        # Récupérer tous les documents de l'utilisateur
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        
        if not documents:
            print("Aucun document trouvé pour cet utilisateur")
            return
        
        print(f"Traitement de {len(documents)} documents...")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = []
        
        for doc in documents:
            print(f"  - Traitement de {doc.filename}")
            
            filepath = doc.filepath.replace('./rag-files/', '../rag-files/')
            
            if not os.path.exists(filepath):
                print(f"    ⚠️  Fichier {filepath} non trouvé, ignoré")
                continue
            
            try:
                # Charger le document selon son type
                if filepath.endswith('.pdf'):
                    loader = PyPDFLoader(filepath)
                elif filepath.endswith('.txt'):
                    loader = TextLoader(filepath)
                else:
                    print(f"    ⚠️  Type de fichier non supporté: {filepath}")
                    continue
                
                docs_to_process = loader.load()
                splits = text_splitter.split_documents(docs_to_process)
                if doc.filename == "1- JavaScript.pdf" and splits:
                    print("\n--- Exemples de chunks extraits de 1- JavaScript.pdf ---")
                    for i, split in enumerate(splits[:5]):  # Afficher les 5 premiers chunks
                        print(f"\n--- Chunk {i+1} ---")
                        print(split.page_content[:300])
                        print("--- Fin du chunk ---")
                    print("\n")
                all_splits.extend(splits)
                print(f"    ✅ {len(splits)} chunks créés")
                
            except Exception as e:
                print(f"    ❌ Erreur lors du traitement de {doc.filename}: {e}")
        
        if all_splits:
            # Ajouter tous les chunks à la base vectorielle
            vectorstore.add_documents(documents=all_splits)
            print(f"✅ Base vectorielle reconstruite avec {len(all_splits)} chunks")
        else:
            print("❌ Aucun chunk à ajouter")
            
    except Exception as e:
        print(f"Erreur lors de la reconstruction: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Reconstruire pour l'utilisateur 1
    rebuild_user_vectorstore(1) 