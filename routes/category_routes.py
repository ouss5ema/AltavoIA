from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from models.category import Category
from models.product import Product

category_bp = Blueprint('categories', __name__)

@category_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """Obtenir toutes les catégories"""
    try:
        status = request.args.get('status', type=int)
        
        query = Category.query
        
        if status is not None:
            query = query.filter_by(status=status)
        
        categories = query.all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        print(f"Get categories error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not retrieve categories'
        }), 500

@category_bp.route('/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """Obtenir une catégorie spécifique"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({
                'error': 'Not Found',
                'message': 'Category not found'
            }), 404
        
        return jsonify({
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Get category error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not retrieve category'
        }), 500

@category_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """Créer une nouvelle catégorie"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Name is required'
            }), 400
        
        # Vérifier si la catégorie existe déjà
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Category with this name already exists'
            }), 400
        
        # Créer la catégorie
        category = Category(
            name=name,
            description=description,
            created_by=current_user_id,
            status=data.get('status', 1)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create category error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not create category'
        }), 500

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Mettre à jour une catégorie"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        category = Category.query.get(category_id)
        if not category:
            return jsonify({
                'error': 'Not Found',
                'message': 'Category not found'
            }), 404
        
        # Vérifier si le nouveau nom existe déjà
        if 'name' in data and data['name'].strip() != category.name:
            existing_category = Category.query.filter_by(name=data['name'].strip()).first()
            if existing_category:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Category with this name already exists'
                }), 400
        
        # Mettre à jour les champs
        if 'name' in data:
            category.name = data['name'].strip()
        if 'description' in data:
            category.description = data['description'].strip()
        if 'status' in data:
            category.status = data['status']
        
        category.updated_by = current_user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update category error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not update category'
        }), 500

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Supprimer une catégorie (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        
        category = Category.query.get(category_id)
        if not category:
            return jsonify({
                'error': 'Not Found',
                'message': 'Category not found'
            }), 404
        
        # Vérifier s'il y a des produits dans cette catégorie
        products_count = Product.query.filter_by(category_id=category_id, status=1).count()
        if products_count > 0:
            return jsonify({
                'error': 'Bad Request',
                'message': f'Cannot delete category. There are {products_count} active products in this category.'
            }), 400
        
        # Soft delete
        category.status = 0
        category.updated_by = current_user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Category deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete category error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not delete category'
        }), 500

@category_bp.route('/<int:category_id>/products', methods=['GET'])
@jwt_required()
def get_category_products(category_id):
    """Obtenir tous les produits d'une catégorie"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', type=int)
        
        # Vérifier si la catégorie existe
        category = Category.query.get(category_id)
        if not category:
            return jsonify({
                'error': 'Not Found',
                'message': 'Category not found'
            }), 404
        
        # Construire la requête
        query = Product.query.filter_by(category_id=category_id)
        
        if status is not None:
            query = query.filter_by(status=status)
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        products = pagination.items
        
        return jsonify({
            'category': category.to_dict(),
            'products': [product.to_dict() for product in products],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        print(f"Get category products error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not retrieve category products'
        }), 500 