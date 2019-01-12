import json
from http import HTTPStatus

from flask import Flask, request
from sqlalchemy import exists
from sqlalchemy_utils import database_exists

from database.database import db_session, init_db, Base
from database.models.models import (
    Allergen, Customer, FoodProduct, Group, Material, Product, ProductComponent, Tag
)
from utils import get_or_create, get_or_create_multiple

app = Flask(__name__)

GROUPS = {
    'food': 'family',
    'textiles': 'range'
}

if not database_exists('sqlite:///products.db'):
    init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def get_class_by_tablename(tablename):
    """Return class reference mapped to table.
    :param tablename: str, String with name of table.
    :return: Class reference or None.
    """
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


@app.route('/products', methods=['GET', 'POST'])
def products():
    api_key = request.headers['X-API-KEY']
    print(api_key)
    if request.method == 'POST':
        json_data = request.get_json()
        if json_data is None:
            print('no json data')
            return 'No JSON body supplied', HTTPStatus.BAD_REQUEST
        print(json_data)

        product_name = json_data.get('name')
        print(product_name)
        if product_name and db_session.query(exists().where(Product.name == product_name)).scalar():
            return 'Product already in database'


        # create common objects for product
        group, _ = get_or_create(db_session, Group, name=GROUPS[api_key])

        tag_names = json_data.get('tags')
        tags = get_or_create_multiple(db_session, Tag, data=tag_names)

        # product_type = get_or_create(db_session, ProductType, name=api_key)

        product_components = json_data.get('billOfMaterials')
        materials = []
        # for key in product_components:
        #     pass

        # if product_type = db_session.query(ProductType).filter_by(name='food').one()
        product_class = get_class_by_tablename(f'{api_key}_products')
        print('product class', product_class)









        tag = Tag(name='test_tag_113')
        # product_type = db_session.query(ProductType).filter_by(name='food').one()
        # product_type = ProductType(name='food')
        material = Material(name='Sugar', units='grams')
        group = Group(name='Fizzy Drinks')
        customer = Customer(name='Sainsbury')
        allergen = Allergen(name='Chili')
        db_session.add_all([tag, group, material, customer, allergen])
        # db_session.add(product_type)
        food_product = FoodProduct(name='Sprite', group=group, customer=customer)

        food_product.tags.append(tag)
        db_session.add(food_product)
        db_session.commit()
        product_component = ProductComponent(material=material, quantity=2.1, product_id=food_product.id)
        db_session.add(product_component)
        db_session.commit()

        food_product.allergens.append(allergen)
        db_session.add(food_product)
        db_session.commit()


        # Create product here

        return 'Product created', HTTPStatus.CREATED
    else:
        # Retrieve all products here
        retrieved_products = []
        return json.dumps(retrieved_products)
