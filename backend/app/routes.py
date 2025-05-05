from flask import Blueprint, jsonify, request
from app.models import Item
from app import db

main = Blueprint('main', __name__)

@main.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])

@main.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
        
    new_item = Item(
        name=data.get('name'),
        description=data.get('description')
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify(new_item.to_dict()), 201