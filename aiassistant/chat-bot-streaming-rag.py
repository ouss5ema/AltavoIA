# chat-bot-streaming-rag.py

from dotenv import load_dotenv
import argparse
import os
import time

from langchain import hub
from langchain_mistralai import ChatMistralAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings.ovhcloud import OVHCloudEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Retrieve OVHcloud AI Endpoints configuration from .env
_OVH_AI_ENDPOINTS_ACCESS_TOKEN = os.environ.get('OVH_AI_ENDPOINTS_ACCESS_TOKEN')
_OVH_AI_ENDPOINTS_MODEL_NAME = os.environ.get('OVH_AI_ENDPOINTS_MODEL_NAME')
_OVH_AI_ENDPOINTS_MODEL_URL = os.environ.get('OVH_AI_ENDPOINTS_MODEL_URL')
_OVH_AI_ENDPOINTS_EMBEDDING_MODEL_NAME = os.environ.get('OVH_AI_ENDPOINTS_EMBEDDING_MODEL_NAME')

def chat_completion(new_message: str):
    # Load the OVHcloud-hosted Mistral model
    model = ChatMistralAI(
        model=_OVH_AI_ENDPOINTS_MODEL_NAME,
        api_key=_OVH_AI_ENDPOINTS_ACCESS_TOKEN,
        endpoint=_OVH_AI_ENDPOINTS_MODEL_URL,
        max_tokens=1500,
        streaming=True
    )

    # Load documents from rag-files folder
    loader = DirectoryLoader(
        path="./rag-files/",
        glob="**/*",
        show_progress=True
    )
    docs = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    # Create embedding model and vectorstore
    embedding_model = OVHCloudEmbeddings(
        model_name=_OVH_AI_ENDPOINTS_EMBEDDING_MODEL_NAME,
        access_token=_OVH_AI_ENDPOINTS_ACCESS_TOKEN
    )
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model
    )

    # Use similarity search (no strict threshold)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Manually fetch docs with scores to decide on fallback
    docs_with_score = vectorstore.similarity_search_with_relevance_scores(new_message, k=4)
    

    # Display scores for debug
    # for doc, score in docs_with_score:
    #     print(f"🔍 Score: {score:.4f} | Preview: {doc.page_content[:60]}")

    if not docs_with_score or all(score < 0.1 for _, score in docs_with_score):
        print("📭 Aucun contexte pertinent. Réponse directe du modèle.\n🤖: ", end="", flush=True)
        for chunk in model.stream(new_message):
            print(chunk.content, end="", flush=True)
            time.sleep(0.15)
        print()
        return

    # RAG Mode
    prompt = hub.pull("rlm/rag-prompt")
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
    )

    print("📄 Contexte trouvé. Réponse avec RAG.\n🤖: ", end="", flush=True)
    for r in rag_chain.stream({"question": new_message}):
        print(r.content, end="", flush=True)
        time.sleep(0.15)
    print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', type=str, default="What is the meaning of life?")
    args = parser.parse_args()
    chat_completion(args.question)

if __name__ == '__main__':
    main()
