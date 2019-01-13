# CONFIG KEYS AND NAMES

# Industry API keys - add any new industries here first.
FOOD = 'food'
TEXTILES = 'textiles'
INDUSTRY_KEYS = [FOOD, TEXTILES]

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

# object group keys
INDEPENDENT = 'independent'
FOOD_PRODUCT = 'food_product'
TEXTILES_PRODUCT = 'textiles_product'
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
    TEXTILES_PRODUCT: TEXTILES_PRODUCT,
}

# product config keys
ALL_FIELDS = 'all_fields'  # all fields required for the product as they come through json.
BASE_FIELDS = 'base_fields'  # minimum set of fields that the product needs to be saved to the db.
MULTI_RELATIONS = 'multi_relations'  # fields which are to be added as multiple product relations.
SINGLE_RELATIONS = 'single_relations'  # all fields to add as product's related fields once their objects are persisted.
PRODUCT_GROUP = 'product_group'  # conversion from customer name for the group to system name (i.e family = group)

PRODUCT_CONFIG = {
    FOOD: {
        ALL_FIELDS: [NAME, TAGS, FAMILY, CUSTOMER, BILL_OF_MATERIALS, ALLERGENS],
        BASE_FIELDS: [NAME, GROUP, CUSTOMER],
        INDEPENDENT: [TAGS, GROUP, CUSTOMER],
        SINGLE_RELATIONS: [GROUP, CUSTOMER],
        PRODUCT_DEPENDENT: [MATERIALS],
        INDUSTRY_DEPENDENT: [ALLERGENS],
        PRODUCT_GROUP: FAMILY,
        MULTI_RELATIONS: [TAGS, MATERIALS]
    },
    TEXTILES: {
        ALL_FIELDS: [NAME, TAGS, RANGE, BILL_OF_MATERIALS, COLOUR],
        BASE_FIELDS: [NAME, GROUP, COLOUR],
        INDEPENDENT: [TAGS, GROUP],
        SINGLE_RELATIONS: [GROUP],
        PRODUCT_DEPENDENT: [MATERIALS],
        INDUSTRY_DEPENDENT: None,
        PRODUCT_GROUP: RANGE,
        MULTI_RELATIONS: [TAGS, MATERIALS]
    }
}

# API messages keys
UNKNOWN_API_KEY = 'unknown_api_key'
DUPLICATE_PRODUCT = 'duplicate_product'
PRODUCT_CREATED = 'product_created'
NO_JSON = 'no_json'
INCORRECT_DATA = 'incorrect_data'

MESSAGES = {
    UNKNOWN_API_KEY: 'Unknown API key. Please check your API key.',
    DUPLICATE_PRODUCT: 'Product already in database, use PUT or PATCH methods to amend.',
    PRODUCT_CREATED: 'Product created',
    NO_JSON: 'No JSON body supplied',
    INCORRECT_DATA: 'Incorrect product data supplied.'
}
