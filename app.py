import json
from http import HTTPStatus

from flask import Flask, request
from sqlalchemy import exists
from sqlalchemy_utils import database_exists, get_class_by_table

from database.database import db_session, init_db, Base
from database.models.models import (
    Allergen, Customer, FoodProduct, Group, Material, Product, ProductComponent, ProductType, Tag
)
app = Flask(__name__)

if not database_exists('sqlite:///products.db'):
    init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/products', methods=['GET', 'POST'])
def products():
    api_key = request.headers['X-API-KEY']
    print(api_key)
    if request.method == 'POST':
        json_data = request.get_json()
        print(json_data)

        # create common objects for product
        # if name in database abort
        # ret = db_session.query(exists().where(SomeObject.field == value)).scalar()
        # if product_type = db_session.query(ProductType).filter_by(name='food').one()
        # product_class = get_class_by_table(Base, f'{api_key}_products')
        # print(product_class)









        tag = Tag(name='test_tag_113')
        # product_type = db_session.query(ProductType).filter_by(name='food').one()
        product_type = ProductType(name='food')
        material = Material(name='Sugar', units='grams')
        group = Group(name='Fizzy Drinks')
        customer = Customer(name='Sainsbury')
        allergen = Allergen(name='Chili')
        db_session.add_all([tag, group, product_type, material, customer, allergen])
        # db_session.add(product_type)
        db_session.commit()
        product = Product(name='Sprite', product_type=product_type, group=group)
        product.tags.append(tag)
        db_session.add(product)
        db_session.commit()
        product_component = ProductComponent(material=material, quantity=2.1, product_id=product.product_id)
        db_session.add(product_component)
        db_session.commit()

        food_product = FoodProduct(customer=customer, product_id=product.product_id)
        food_product.allergens.append(allergen)
        db_session.add(food_product)
        db_session.commit()
        print(product.product_components)
        if json_data is None:
            print('no json data')
            return 'No JSON body supplied', HTTPStatus.BAD_REQUEST

        # Create product here

        return 'Product created', HTTPStatus.CREATED
    else:
        # Retrieve all products here
        retrieved_products = []
        return json.dumps(retrieved_products)
