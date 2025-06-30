from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from models.product import Product
from models.category import Category
from models.user import User

product_bp = Blueprint('products', __name__)

@product_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """Obtenir tous les produits avec pagination et filtres"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status', type=int)
        
        # Construire la requête
        query = Product.query
        
        # Appliquer les filtres
        if search:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
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
        print(f"Get products error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not retrieve products'
        }), 500

@product_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Obtenir un produit spécifique"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'error': 'Not Found',
                'message': 'Product not found'
            }), 404
        
        return jsonify({
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Get product error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not retrieve product'
        }), 500

@product_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Créer un nouveau produit"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        # Validation des données requises
        required_fields = ['name', 'description', 'price', 'category_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': 'Bad Request',
                    'message': f'{field} is required'
                }), 400
        
        # Vérifier si la catégorie existe
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Category not found'
            }), 400
        
        # Créer le produit
        product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category_id=data['category_id'],
            created_by=current_user_id,
            status=data.get('status', 1)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create product error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not create product'
        }), 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Mettre à jour un produit"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'error': 'Not Found',
                'message': 'Product not found'
            }), 404
        
        # Mettre à jour les champs
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'category_id' in data:
            # Vérifier si la catégorie existe
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Category not found'
                }), 400
            product.category_id = data['category_id']
        if 'status' in data:
            product.status = data['status']
        
        product.updated_by = current_user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update product error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not update product'
        }), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Supprimer un produit (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'error': 'Not Found',
                'message': 'Product not found'
            }), 404
        
        # Soft delete
        product.status = 0
        product.updated_by = current_user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete product error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not delete product'
        }), 500

@product_bp.route('/bulk-delete', methods=['POST'])
@jwt_required()
def bulk_delete_products():
    """Supprimer plusieurs produits en masse"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'product_ids' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Product IDs are required'
            }), 400
        
        product_ids = data['product_ids']
        if not isinstance(product_ids, list):
            return jsonify({
                'error': 'Bad Request',
                'message': 'Product IDs must be a list'
            }), 400
        
        # Soft delete tous les produits
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        
        for product in products:
            product.status = 0
            product.updated_by = current_user_id
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(products)} products deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Bulk delete products error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Could not delete products'
        }), 500 