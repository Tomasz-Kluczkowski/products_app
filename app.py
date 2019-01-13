from http import HTTPStatus

from flask import Flask, request, jsonify
from flask.json import JSONEncoder
from sqlalchemy import exists
from sqlalchemy_utils import database_exists
from sqlalchemy.ext.declarative import DeclarativeMeta

from database.database import db_session, init_db
from database.models.models import Product
from utils import get_or_create, get_or_create_multiple, get_class_by_table_name


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict()
        return super(CustomJSONEncoder, self).default(obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder


# industry keys
FOOD = 'food'
TEXTILES = 'textile'

# product field keys (also some are corresponding table names)
NAME = 'name'
TAGS = 'tags'
FAMILY = 'family'
RANGE = 'range'
CUSTOMER = 'customer'
BILL_OF_MATERIALS = 'billOfMaterials'
MATERIALS = 'materials'
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
PRODUCT_DEPENDENT = 'product_dependent'
INDUSTRY_DEPENDENT = 'industry_dependent'

# convert fields to appropriate application table names
TABLE_NAMES = {
    TAGS: TAG,
    GROUP: GROUP,
    CUSTOMER: CUSTOMER,
    MATERIALS: MATERIAL,
    ALLERGENS: ALLERGEN,
    FOOD_PRODUCT: FOOD_PRODUCT,
    TEXTILE_PRODUCT: TEXTILE_PRODUCT,
}

# field keys required for product relations
RELATED_FIELDS = [TAGS, MATERIALS]

OBJECT_NAMES = {
    INDEPENDENT: [TAGS, GROUP, CUSTOMER],
    PRODUCT_RELATIONS: [TAGS, GROUP, CUSTOMER, MATERIALS, ALLERGENS],
    PRODUCT_DEPENDENT: [MATERIALS],
    INDUSTRY_DEPENDENT: {
        FOOD: [ALLERGENS]
    },
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

    def __init__(self, data, product_type):
        self.data = data
        self.product_type = product_type
        self.objects = {}
        self._cleanse_data()

    def _cleanse_data(self):
        """
        Convert json key names to system names (for family/range -> group and billOfMaterials -> materials).
        """
        product_group = PRODUCT_GROUPS[self.product_type]
        self.data[GROUP] = self.data[product_group]
        self.data[MATERIALS] = self.data[BILL_OF_MATERIALS]

    def _create_base_product(self):
        """
        Creates base product without relationships that require its existence formerly. Needs objects from
        INDEPENDENT object names to exist first. Product is then flushed to the database but not committed.
        :return: product, instance of a product
        """
        product_class = get_class_by_table_name(f'{self.product_type}_product')
        if product_class:
            # build kwargs for product
            product_kwargs = {}
            for field in BASE_FIELDS[f'{self.product_type}_product']:
                if field in OBJECT_NAMES[PRODUCT_RELATIONS]:
                    product_kwargs[field] = self.objects[field]
                else:
                    product_kwargs[field] = self.data[field]
            product, _ = get_or_create(product_class, **product_kwargs)
            db_session.add(product)
            db_session.flush()
            self.objects['product_id'] = product.id
            return product
        raise ValueError('Unknown product class')

    def _create_objects(self, object_names):
        """
        Create objects from a list of object names.
        :param object_names: list, List of object names
        :return:
        """
        for obj_name in object_names:
            if self.data.get(obj_name):
                data = self.data[obj_name]
                multiple = False
                if isinstance(data, list) or isinstance(data, dict):
                    multiple = True
                table_name = TABLE_NAMES[obj_name]
                object_class = get_class_by_table_name(table_name)

                if object_class:
                    if multiple:
                        # inject product id into data dictionary for objects that need it as a field.
                        if obj_name in OBJECT_NAMES[PRODUCT_DEPENDENT]:
                            for key, value in data.items():
                                value['product_id'] = self.objects['product_id']
                        self.objects[obj_name] = get_or_create_multiple(object_class, data=data)
                        db_session.add_all(self.objects[obj_name])
                    else:
                        self.objects[obj_name], _ = get_or_create(object_class, name=self.data[obj_name])
                        db_session.add(self.objects[obj_name])

    def create_product_from_data(self):
        """
        Creates product and required objects it depends on from data.
        """
        # create independent objects first: tags, group (family, range), customer as they do not need
        # anything to exist.
        self._create_objects(OBJECT_NAMES[INDEPENDENT])

        # create product dependencies in database (ids will be needed to save the product object in next step)
        db_session.flush()
        base_product = self._create_base_product()
        # now create common product dependent objects.
        self._create_objects(OBJECT_NAMES[PRODUCT_DEPENDENT])

        # create industry specific dependent objects.
        related_fields = list(RELATED_FIELDS)
        if OBJECT_NAMES[INDUSTRY_DEPENDENT].get(self.product_type):
            industry_dependent_obj_names = OBJECT_NAMES[INDUSTRY_DEPENDENT][self.product_type]
            self._create_objects(industry_dependent_obj_names)
            related_fields.extend(industry_dependent_obj_names)
        # append dependant objects to product
        for field in related_fields:
            # add objects to appropriate fields
            getattr(base_product, field).extend(self.objects[field])
        db_session.commit()


@app.route('/products', methods=['GET', 'POST'])
def products():
    product_type = request.headers['X-API-KEY']
    if request.method == 'POST':
        json_data = request.get_json()
        if json_data is None:
            print('no json data')
            return 'No JSON body supplied', HTTPStatus.BAD_REQUEST
        product_name = json_data.get('name')
        if product_name and db_session.query(exists().where(Product.name == product_name)).scalar():
            return 'Product already in database, use PUT or PATCH methods to amend.'

        product_creator = ProductCreator(data=json_data, product_type=product_type)
        product_creator.create_product_from_data()

        return 'Product created', HTTPStatus.CREATED
    else:
        # Retrieve all products here
        product_class = get_class_by_table_name(f'{product_type}_product')
        if product_class:
            retrieved_products = product_class.query.all()
            return jsonify(retrieved_products)
        return 'No data for this product type found. Please check your API_KEY', HTTPStatus.NOT_FOUND
