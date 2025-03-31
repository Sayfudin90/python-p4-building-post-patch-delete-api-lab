#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries/')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(jsonify(bakeries), 200)

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = db.session.get(Bakery,id)
    
    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    if request.method == 'PATCH':
        form_data = request.form  # Expecting form data, not JSON
        if 'name' in form_data:
            bakery.name = form_data['name']
            db.session.commit()  

            return make_response(jsonify(bakery.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "Missing 'name' field"}), 400)

    return make_response(jsonify(bakery.to_dict()), 200)

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    if request.method == 'POST':
        form_data = request.form  # Expecting form data, not JSON

        # Ensure all required fields are provided
        if not all(k in form_data for k in ['name', 'price', 'bakery_id']):
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        try:
            new_baked_good = BakedGood(
                name=form_data['name'],
                price=float(form_data['price']),  # Convert price to float
                bakery_id=int(form_data['bakery_id'])  # Convert bakery_id to integer
            )

            db.session.add(new_baked_good)
            db.session.commit()
            
            return make_response(jsonify(new_baked_good.to_dict()), 201)
        except ValueError:
            return make_response(jsonify({"error": "Invalid data type for price or bakery_id"}), 400)
    
    return make_response(jsonify([b.to_dict() for b in BakedGood.query.all()]), 200)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def baked_good_by_id(id):
    baked_good = db.session.get(BakedGood, id)
    
    if not baked_good:
        return make_response(jsonify({"error": "Baked good not found"}), 404)
    
    db.session.delete(baked_good)
    db.session.commit()
    
    return make_response(jsonify({"message": "Baked good successfully deleted"}), 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    
    if not most_expensive:
        return make_response(jsonify({"error": "No baked goods found"}), 404)
    
    return make_response(jsonify(most_expensive.to_dict()), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
