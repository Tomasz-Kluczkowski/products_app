from http import HTTPStatus

from flask import Flask, request, jsonify
from flask.json import JSONEncoder
from sqlalchemy import exists
from sqlalchemy_utils import database_exists
from sqlalchemy.ext.declarative import DeclarativeMeta

from database.database import db_session, init_db
from database.models.models import Product
from system_config import (ALL_FIELDS, BASE_FIELDS, BILL_OF_MATERIALS, DUPLICATE_PRODUCT, GROUP, INCORRECT_DATA,
                           INDEPENDENT, INDUSTRY_DEPENDENT, INDUSTRY_KEYS, MATERIALS, MESSAGES, MULTI_RELATIONS,
                           NO_JSON, PRODUCT_CONFIG, PRODUCT_CREATED, PRODUCT_DEPENDENT, PRODUCT_GROUP, SINGLE_RELATIONS,
                           TABLE_NAMES, UNKNOWN_API_KEY)
from utils import get_or_create, get_or_create_multiple, get_class_by_table_name


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict()
        return super(CustomJSONEncoder, self).default(obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

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
        self.product_config = PRODUCT_CONFIG[product_type]

    def get_json_fields(self):
        """
        Obtain a set of json fields supplied by the user.
        :return: set, set of fields in the json data.
        """
        json_fields = set()
        for field in self.data:
            json_fields.add(field)
        return json_fields

    def check_all_fields_present(self, json_fields):
        """
        :param json_fields: set, set of json fields against which we need to make the check.
        Confirm all required fields present in json data supplied by the user.
        :return: bool, True if all fields present, False otherwise.
        """
        all_fields = set(self.product_config[ALL_FIELDS])
        return all_fields == json_fields

    def _cleanse_data(self):
        """
        Convert json field names to system names (for family/range -> group and billOfMaterials -> materials).
        """
        product_group = self.product_config[PRODUCT_GROUP]
        self.data[GROUP] = self.data[product_group]
        del(self.data[product_group])
        self.data[MATERIALS] = self.data[BILL_OF_MATERIALS]
        del(self.data[BILL_OF_MATERIALS])

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
            for field in self.product_config[BASE_FIELDS]:
                if field in self.product_config[SINGLE_RELATIONS]:
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
                        if obj_name in self.product_config[PRODUCT_DEPENDENT]:
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
        # Normalize field names to system names.
        self._cleanse_data()
        # create independent objects first: tags, group (family, range), customer as they do not need
        # anything to exist.
        self._create_objects(self.product_config[INDEPENDENT])

        # create product dependencies in database (ids will be needed to save the product object in next step)
        db_session.flush()
        base_product = self._create_base_product()
        # now create product dependent objects (those need product_id.
        self._create_objects(self.product_config[PRODUCT_DEPENDENT])

        # create industry specific dependent objects.
        multi_relations = self.product_config[MULTI_RELATIONS]
        if self.product_config.get(INDUSTRY_DEPENDENT):
            industry_dependent_relations = self.product_config[INDUSTRY_DEPENDENT]
            self._create_objects(industry_dependent_relations)
            multi_relations.extend(industry_dependent_relations)
        # append dependent objects to product
        for relation in multi_relations:
            # add objects to appropriate fields
            getattr(base_product, relation).extend(self.objects[relation])
        db_session.commit()


@app.route('/products', methods=['GET', 'POST'])
def products():
    product_type = request.headers['X-API-KEY']
    # confirm correct API key used.
    if product_type not in INDUSTRY_KEYS:
        return MESSAGES[UNKNOWN_API_KEY], HTTPStatus.FORBIDDEN
    if request.method == 'POST':
        json_data = request.get_json()
        # Abort if no data supplied.
        if json_data is None:
            return MESSAGES[NO_JSON], HTTPStatus.BAD_REQUEST
        product_name = json_data.get('name')
        # Abort if product already exists.
        if product_name and db_session.query(exists().where(Product.name == product_name)).scalar():
            return MESSAGES[DUPLICATE_PRODUCT], HTTPStatus.BAD_REQUEST

        product_creator = ProductCreator(data=json_data, product_type=product_type)
        # confirm all fields present before doing any work.
        # TODO: add info for customer - which fields are missing in the message.
        json_fields = product_creator.get_json_fields()
        if not product_creator.check_all_fields_present(json_fields):
            return MESSAGES[INCORRECT_DATA], HTTPStatus.BAD_REQUEST

        product_creator.create_product_from_data()

        return MESSAGES[PRODUCT_CREATED], HTTPStatus.CREATED
    else:
        # Retrieve all products here
        product_class = get_class_by_table_name(f'{product_type}_product')
        if product_class:
            retrieved_products = product_class.query.all()
            return jsonify(retrieved_products)
        return MESSAGES[UNKNOWN_API_KEY], HTTPStatus.NOT_FOUND
