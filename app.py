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

# product field keys (also some are corresponding table names)
NAME = 'name'
TAGS = 'tags'
FAMILY = 'family'
RANGE = 'range'
CUSTOMER = 'customer'
BILL_OF_MATERIALS = 'billOfMaterials'
ALLERGENS = 'allergens'
COLOUR = 'colour'
GROUP = 'group'

# singular table keys
TAG = 'tag'
PRODUCT_COMPONENT = 'product_component'
ALLERGEN = 'allergen'
MATERIAL = 'material'
PRODUCT = 'product'

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

# convert json keys to appropriate application table names
TABLE_NAMES = {
    TAGS: TAG,
    GROUP: GROUP,
    CUSTOMER: CUSTOMER,
    BILL_OF_MATERIALS: MATERIAL,
    ALLERGENS: ALLERGEN,
    FOOD_PRODUCT: FOOD_PRODUCT,
    TEXTILE_PRODUCT: TEXTILE_PRODUCT,
}

OBJECT_NAMES = {
    INDEPENDENT: [(TAGS,), GROUP, CUSTOMER],
    PRODUCT_RELATIONS: [TAGS, GROUP, CUSTOMER, BILL_OF_MATERIALS, ALLERGENS],
    COMMON_DEPENDENT: [(BILL_OF_MATERIALS, )],
    FOOD_DEPENDENT: [(ALLERGENS, )],
}

BASE_FIELDS = {
    FOOD_PRODUCT: [NAME, GROUP, CUSTOMER],
    TEXTILE_PRODUCT: [NAME, GROUP, COLOUR],
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

    def __init__(self,data, product_type):
        self.data = data
        self.product_type = product_type
        self.objects = {}
        self._unify_groups()
        
    def _unify_groups(self):
        """
        Saves any value belonging to a group like field on a common for all products group key.
        """
        product_group = PRODUCT_GROUPS[self.product_type]
        self.data[GROUP] = self.data[product_group]

    def _create_base_product(self):
        """
        Creates base product without relationships that require its existence formerly. Needs objects from
        INDEPENDENT object names to exist first. Product is then flushed to the database but not committed.
        """
        product_class = get_class_by_table_name(f'{self.product_type}_products')
        if product_class:
            # build kwargs for product
            product_kwargs = {}
            for field in BASE_FIELDS[f'{self.product_type}_product']:
                if field in OBJECT_NAMES[PRODUCT_RELATIONS]:
                    product_kwargs[field] = self.objects[field]
                else:
                    product_kwargs[field] = self.data[field]
            product = get_or_create(product_kwargs, **product_kwargs)
            db_session.add(product)
            db_session.flush()

    def create_product_from_data(self):
        """
        Creates product and required objects it depends on from data.
        """
        # create independent objects first: tags, group (family, range), customer as they do not need
        # anything to exist.
        for obj_name in OBJECT_NAMES[INDEPENDENT]:
            multiple = False
            if isinstance(obj_name, tuple):
                multiple = True
                obj_name = obj_name[0]

            table_name = TABLE_NAMES[obj_name]
            object_class = get_class_by_table_name(table_name)

            if self.data.get(obj_name) and object_class:
                if multiple:
                    self.objects[obj_name] = get_or_create_multiple(object_class, data=self.data[obj_name])
                    db_session.add_all(self.objects[obj_name])
                else:
                    # here in case in the future our independent models need more than just the name we will
                    # need to build object kwargs same as for the products.
                    self.objects[obj_name] = get_or_create(object_class, name=self.data[obj_name])
                    db_session.add(self.objects[obj_name])

        # create product dependencies in database (ids will be needed to save the product object in next step)
        db_session.flush()
        self._create_base_product()




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
        # for key in PRODUCT_GROUPS.values():
        #     if json_data.get(key):
        #         json_data[GROUPS]

        product_name = json_data.get('name')
        print(product_name)
        # Here we will need to create a possibility of inserting many objects at once. For now only one.
        if product_name and db_session.query(exists().where(Product.name == product_name)).scalar():
            return 'Product already in database'


        # create common objects for product
        group, _ = get_or_create(Group, name=json_data[PRODUCT_GROUPS[api_key]])

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
