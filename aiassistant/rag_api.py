from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import json
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Tuple
import sys

# --- NOUVELLE GESTION DE LA BASE DE DONNÉES ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importer les modèles nécessaires
from models.user import User
from models.document import Document
# ----------------------------------------------

from langchain_mistralai import ChatMistralAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings.ovhcloud import OVHCloudEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# --- Validation des variables d'environnement ---
required_env_vars = [
    "OVH_AI_ENDPOINTS_ACCESS_TOKEN",
    "OVH_AI_ENDPOINTS_MODEL_NAME",
    "OVH_AI_ENDPOINTS_MODEL_URL",
    "OVH_AI_ENDPOINTS_EMBEDDING_MODEL_NAME",
    "JWT_SECRET_KEY"
]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"Erreur: Les variables d'environnement suivantes sont manquantes ou vides : {', '.join(missing_vars)}")
    print("Veuillez vérifier votre fichier .env à la racine du projet.")
    sys.exit(1)

# --- Configuration ---
_OVH_AI_ENDPOINTS_ACCESS_TOKEN = os.getenv('OVH_AI_ENDPOINTS_ACCESS_TOKEN')
_OVH_AI_ENDPOINTS_MODEL_NAME = os.getenv('OVH_AI_ENDPOINTS_MODEL_NAME')
_OVH_AI_ENDPOINTS_MODEL_URL = os.getenv('OVH_AI_ENDPOINTS_MODEL_URL')
_OVH_AI_ENDPOINTS_EMBEDDING_MODEL_NAME = os.getenv('OVH_AI_ENDPOINTS_EMBEDDING_MODEL_NAME')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this')
ALGORITHM = "HS256"

# --- Initialisation de la base de données pour l'API RAG (MÉTHODE ROBUSTE) ---
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:@localhost/altavo_partners'
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# --- Fin de l'initialisation de la base de données ---

# --- Prompt Système ---
SYSTEM_PROMPT = """Tu es Altavo AI, un assistant expert, polyvalent et serviable. Ton objectif principal est de fournir des réponses précises, professionnelles, et grammaticalement parfaites.
- Rédige toutes tes réponses en français impeccable, sans aucune faute.
- Ne coupe JAMAIS tes mots. Termine toujours les mots que tu commences.
- Adopte un ton poli et professionnel.
- Quand tu fournis du code, tu le retournes dans des blocs de code formatés avec le nom du langage (par exemple, ```python).
- N'invente pas d'informations. Si tu ne connais pas la réponse, dis-le clairement."""

# --- Initialisation du Modèle et Embeddings (sans vectorstore global) ---
model = ChatMistralAI(
    model=_OVH_AI_ENDPOINTS_MODEL_NAME,
    mistral_api_key=_OVH_AI_ENDPOINTS_ACCESS_TOKEN,
    endpoint=_OVH_AI_ENDPOINTS_MODEL_URL,
    temperature=0.2,
    max_tokens=2048,
    top_k=40,
    top_p=0.9,
    streaming=True
)
embedding_model = OVHCloudEmbeddings(
    model_name=_OVH_AI_ENDPOINTS_EMBEDDING_MODEL_NAME,
    access_token=_OVH_AI_ENDPOINTS_ACCESS_TOKEN
)

# --- Configuration ---
CHROMA_DB_PATH = "./chroma_db" # Dossier pour stocker les bases vectorielles

# --- API FastAPI ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Dépendances d'Authentification ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# --- Fonctions utilitaires RAG par utilisateur ---
def get_user_vectorstore(user: User):
    # Charge la base de données vectorielle persistante de l'utilisateur
    # Si elle n'existe pas, une nouvelle sera créée implicitement lors de l'upload.
    try:
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            collection_name=f"user_{user.id}_collection",
            embedding_function=embedding_model
        )
        return vectorstore
    except Exception as e:
        # Gérer le cas où la collection n'existe pas encore etc.
        print(f"Could not load vector store for user {user.id}: {e}")
        return None

class AskPayload(BaseModel):
    question: str
    history: List[Tuple[str, str]] = []

def format_docs(docs):
    return "\\n\\n".join(doc.page_content for doc in docs)

def format_history(history: List[Tuple[str, str]]) -> str:
    buffer = ""
    for role, content in history:
        if role.lower() == 'user':
            buffer += f"Humain: {content}\\n"
        elif role.lower() == 'assistant':
            buffer += f"Assistant: {content}\\n"
    return buffer

@app.post("/ask")
async def ask_question(payload: AskPayload, current_user: User = Depends(get_current_user)):
    question = payload.question
    history_str = format_history(payload.history)
    
    vectorstore = get_user_vectorstore(current_user)
    relevant_docs = []
    use_rag = False
    SIMILARITY_THRESHOLD = 1.0 # À ajuster selon la métrique de ta base (plus bas = plus strict)

    if vectorstore:
        try:
            docs_and_scores = vectorstore.similarity_search_with_score(question, k=3)
            # Filtrer les documents vraiment pertinents
            filtered = [(doc, score) for doc, score in docs_and_scores if score < SIMILARITY_THRESHOLD]
            if filtered:
                relevant_docs = [doc for doc, score in filtered]
                use_rag = True
            else:
                use_rag = False
        except Exception as e:
            use_rag = False

    async def sse_generator(chain, input_data, mode):
        yield f"data: {json.dumps({'type': 'mode', 'value': mode})}\n\n"
        full_response = ""
        for chunk in chain.stream(input_data):
            if hasattr(chunk, 'content'):
                token = chunk.content
            else:
                token = str(chunk)
            if token:
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'value': token})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'full_response': full_response})}\n\n"

    if use_rag and relevant_docs:
        context = format_docs(relevant_docs)
        template = SYSTEM_PROMPT + "\n\nContexte:{context}\n\nHistorique:\n{chat_history}Humain: {question}\nAssistant:"
        prompt = PromptTemplate.from_template(template)
        chain = prompt | model
        input_data = {"context": context, "question": question, "chat_history": history_str}
        return StreamingResponse(sse_generator(chain, input_data, "RAG"), media_type="text/event-stream")
    else:
        template = SYSTEM_PROMPT + "\n\nHistorique:\n{chat_history}Humain: {question}\nAssistant:"
        prompt = PromptTemplate.from_template(template)
        chain = prompt | model
        input_data = {"question": question, "chat_history": history_str}
        return StreamingResponse(sse_generator(chain, input_data, "fallback"), media_type="text/event-stream")

# --- Endpoints d'Upload et de listing ---
UPLOAD_DIR_BASE = "./rag-files/"
ALLOWED_EXTENSIONS = {"pdf", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_upload_dir = os.path.join(UPLOAD_DIR_BASE, f"user_{current_user.id}")
    if not os.path.exists(user_upload_dir):
        os.makedirs(user_upload_dir)

    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        collection_name=f"user_{current_user.id}_collection",
        embedding_function=embedding_model
    )
    
    saved_files_info = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for file in files:
        # --- VALIDATIONS RÉINTÉGRÉES ---
        ext = file.filename.split(".")[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Extension non autorisée: {file.filename}")
        
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"Fichier trop volumineux: {file.filename}")

        save_path = os.path.join(user_upload_dir, file.filename)
        if os.path.exists(save_path):
            raise HTTPException(status_code=409, detail=f"Un fichier avec le nom '{file.filename}' existe déjà.")
        # --- FIN DES VALIDATIONS ---

        with open(save_path, "wb") as f:
            f.write(contents)
        
        if save_path.endswith((".pdf", ".txt")):
            loader = PyPDFLoader(save_path) if save_path.endswith(".pdf") else TextLoader(save_path)
            docs_to_process = loader.load()
            splits = text_splitter.split_documents(docs_to_process)
            if splits:
                vectorstore.add_documents(documents=splits)

        new_document = Document(
            user_id=current_user.id,
            filename=file.filename,
            filepath=save_path
        )
        db.add(new_document)
        db.commit()
        
        saved_files_info.append({"filename": file.filename, "id": new_document.id})
    
    # La persistance est gérée automatiquement par ChromaDB lorsqu'un
    # persist_directory est fourni. L'appel explicite n'est plus nécessaire.
    # vectorstore.persist()

    return {"success": True, "files": saved_files_info}

@app.get("/documents")
async def list_documents(current_user: User = Depends(get_current_user)):
    user_docs = current_user.documents
    return {"files": [{"filename": doc.filename, "id": doc.id} for doc in user_docs]}

@app.delete("/documents/{document_id}")
async def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette ressource.")

    try:
        if os.path.exists(document.filepath):
            os.remove(document.filepath)
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier physique {document.filepath}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de la suppression du fichier.")

    db.delete(document)
    db.commit()
    
    # La logique de reconstruction de ChromaDB est retirée pour l'instant pour simplifier.
    # rebuild_user_vectorstore(current_user, db)

    return {"success": True, "message": f"Document '{document.filename}' supprimé avec succès."}

# La fonction rebuild_user_vectorstore est retirée car non utilisée pour le moment.
