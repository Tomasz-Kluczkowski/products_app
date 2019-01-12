import json
from http import HTTPStatus

from flask import Flask, request
from sqlalchemy import exists
from sqlalchemy_utils import database_exists

from database.database import db_session, init_db
from database.models.models import (
    Allergen, Customer, FoodProduct, Group, Material, Product, ProductComponent, Tag
)
from utils import get_or_create, get_or_create_multiple, get_class_by_table_name

app = Flask(__name__)

# industry keys
FOOD = 'food'
TEXTILES = 'textiles'

#product field keys
NAME = 'name'
TAGS = 'tags'
FAMILY = 'family'
RANGE = 'range'
CUSTOMER = 'customer'
BILL_OF_MATERIALS = 'billOfMaterials'
ALLERGENS = 'allergens'
COLOUR = 'colour'
GROUPS = 'groups'

PRODUCT_GROUPS = {
    FOOD: FAMILY,
    TEXTILES: RANGE
}

# object group keys
PRODUCT_RELATIONS = 'product_relations'
INDEPENDENT = 'independent'
FOOD_PRODUCT = 'food_product'
TEXTILE_PRODUCT = 'textile_product'
COMMON_DEPENDENT = 'common_dependent'
FOOD_DEPENDENT = 'food_dependent'


PRODUCT_KEYS = {
    PRODUCT_RELATIONS: [TAGS, FAMILY, RANGE, CUSTOMER, BILL_OF_MATERIALS, ALLERGENS],
    INDEPENDENT: [(TAGS, ), FAMILY, RANGE, CUSTOMER],
    FOOD_PRODUCT: [NAME, FAMILY, CUSTOMER],
    TEXTILE_PRODUCT: [NAME, RANGE, COLOUR],
    COMMON_DEPENDENT: [(BILL_OF_MATERIALS, )],
    FOOD_DEPENDENT: [(ALLERGENS, )],
}


if not database_exists('sqlite:///products.db'):
    init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


class ProductCreator:
    """
    Use this class to ease product creation.
    """

    def __init__(self):
        self.objects = {}

    def create_product_from_data(self, data, product_type):
        """
        Creates product and required objects it depends on from data.
        :param data: dict, Decoded json product data.
        :param product_type: str, Type of product to create (i.e food, textile.) - use api key.
        :return:
        """
        # create independent objects first: tags, group (family, range), customer as they do not need
        # anything to exist.
        for item in PRODUCT_KEYS[INDEPENDENT]:
            multiple = False
            key = item
            if isinstance(item, tuple):
                multiple = True
                key = item[0]

            table_name = key
            if key in PRODUCT_GROUPS.values():
                table_name = 'groups'
            object_class = get_class_by_table_name(table_name)

            if data.get(key) and object_class:
                if multiple:
                    self.objects[key] = get_or_create_multiple(object_class, data=data[key])
                    db_session.add_all(self.objects[key])
                else:
                    self.objects[key] = get_or_create(object_class, data=data[key])
                    db_session.add(self.objects[key])

        # create product dependencies in database (ids will be needed to save the product object in next step)
        db_session.flush()
        product_class = get_class_by_table_name(f'{product_type}_products')
        # build kwargs for product
        product_kwargs = {}
        for item in PRODUCT_KEYS[f'{product_type}_product']:
            if item in PRODUCT_KEYS[PRODUCT_RELATIONS]:

            product_kwargs[item] =
        if product_class:
            product =





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
        # copy family or range into group key (makes everything uniform later on).
        for key in PRODUCT_GROUPS.values():
            if json_data.get(key):
                json_data[GROUPS]

        product_name = json_data.get('name')
        print(product_name)
        # Here we will need to create a possibility of inserting many objects at once. For now only one.
        if product_name and db_session.query(exists().where(Product.name == product_name)).scalar():
            return 'Product already in database'


        # create common objects for product
        group, _ = get_or_create(Group, name=GROUPS[api_key])

        tag_names = json_data.get('tags')
        tags = get_or_create_multiple(Tag, data=tag_names)

        # product_type = get_or_create(db_session, ProductType, name=api_key)

        product_components = json_data.get('billOfMaterials')
        materials = []
        # for key in product_components:
        #     pass

        # if product_type = db_session.query(ProductType).filter_by(name='food').one()
        product_class = get_class_by_table_name(f'{api_key}_products')
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
