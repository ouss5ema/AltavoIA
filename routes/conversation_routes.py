from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Conversation, Message, User
from config.database import db
from sqlalchemy import desc, asc

conversation_bp = Blueprint('conversation_bp', __name__)

# Endpoint pour lister toutes les conversations de l'utilisateur
@conversation_bp.route('/', methods=['GET'])
@jwt_required()
def get_conversations():
    user_id = get_jwt_identity()
    conversations = Conversation.query.filter_by(user_id=user_id).order_by(
        Conversation.is_pinned.desc(), 
        Conversation.created_at.desc()
    ).all()
    return jsonify([conv.to_dict() for conv in conversations]), 200

# Endpoint pour créer une nouvelle conversation
@conversation_bp.route('/', methods=['POST'])
@jwt_required()
def create_conversation():
    user_id = get_jwt_identity()
    data = request.json
    
    # Le premier message de l'utilisateur
    first_message_content = data.get('message')
    if not first_message_content:
        return jsonify({"message": "Le premier message est requis"}), 400

    # Optionnel: un titre pour la conversation
    title = data.get('title')
    if not title:
        # Générer un titre court à partir du premier message
        title = (first_message_content[:40] + '...') if len(first_message_content) > 40 else first_message_content
    
    new_conv = Conversation(user_id=user_id, title=title)
    db.session.add(new_conv)
    db.session.commit() # Commit pour obtenir l'ID de la conversation

    # Enregistrer le premier message de l'utilisateur
    user_message = Message(conversation_id=new_conv.id, sender='user', content=first_message_content)
    db.session.add(user_message)

    # Enregistrer la première réponse de l'IA
    ai_response_content = data.get('ai_response')
    if ai_response_content:
        ai_message = Message(conversation_id=new_conv.id, sender='ai', content=ai_response_content)
        db.session.add(ai_message)

    db.session.commit()
    
    return jsonify(new_conv.to_dict()), 201

# Endpoint pour récupérer les messages d'une conversation
@conversation_bp.route('/<int:conv_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conv_id):
    user_id = get_jwt_identity()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first_or_404('Conversation non trouvée')
    messages = Message.query.filter_by(conversation_id=conv.id).order_by(Message.created_at.asc()).all()
    return jsonify([msg.to_dict() for msg in messages]), 200

# Endpoint pour ajouter des messages à une conversation
@conversation_bp.route('/<int:conv_id>/messages', methods=['POST'])
@jwt_required()
def add_message(conv_id):
    user_id = get_jwt_identity()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first_or_404('Conversation non trouvée')
    
    data = request.json
    user_message_content = data.get('user_message')
    ai_response_content = data.get('ai_response')

    if not user_message_content or not ai_response_content:
        return jsonify({"message": "Le message de l'utilisateur et de l'IA sont requis"}), 400

    # Enregistrer le message de l'utilisateur
    user_msg = Message(conversation_id=conv.id, sender='user', content=user_message_content)
    db.session.add(user_msg)
    
    # Enregistrer la réponse de l'IA
    ai_msg = Message(conversation_id=conv.id, sender='ai', content=ai_response_content)
    db.session.add(ai_msg)

    db.session.commit()
    
    return jsonify({"message": "Messages ajoutés avec succès"}), 201

# Endpoint pour supprimer une conversation
@conversation_bp.route('/<int:conv_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conv_id):
    user_id = get_jwt_identity()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    
    if not conv:
        return jsonify({"message": "Conversation non trouvée ou non autorisée"}), 404
        
    db.session.delete(conv)
    db.session.commit()
    
    return jsonify({"message": "Conversation supprimée avec succès"}), 200

# Endpoint pour renommer une conversation
@conversation_bp.route('/<int:conv_id>/rename', methods=['PUT'])
@jwt_required()
def rename_conversation(conv_id):
    user_id = get_jwt_identity()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first_or_404('Conversation non trouvée')
    
    data = request.json
    new_title = data.get('title')

    if not new_title or len(new_title.strip()) == 0:
        return jsonify({"message": "Le titre ne peut pas être vide"}), 400

    conv.title = new_title.strip()
    db.session.commit()
    
    return jsonify(conv.to_dict()), 200

# Endpoint pour épingler/désépingler une conversation
@conversation_bp.route('/<int:conv_id>/pin', methods=['PUT'])
@jwt_required()
def pin_conversation(conv_id):
    user_id = get_jwt_identity()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first_or_404('Conversation non trouvée')
    
    # Inverser le statut "épinglé"
    conv.is_pinned = not conv.is_pinned
    db.session.commit()
    
    return jsonify(conv.to_dict()), 200 