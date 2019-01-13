# Flask Skeleton App

## Installation
Create a [virtualenvironment](https://virtualenv.pypa.io/en/latest/) using Python 3 for the app. We recommend using 
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):
```bash
mkvirtualenv flask-skeleton
```
Then install the dependencies:
```bash
pip install -r requirements.txt
```
## Running
The Flask app can be run by doing:
```bash
FLASK_APP=app.py  FLASK_ENV=development flask run
```

## Test adding product after new database created
```bash
# food product
curl localhost:5000/products -d '{"name": "Chorizo", "tags": ["spicy", "spanish"], "customer": "Deans Butchers", "family": "sausage", "allergens": ["cereals"], "billOfMaterials": {"paprika": {"quantity": 100, "units": "tablespoons"}, "pork mince": {"quantity": 10, "units": "kg"}}}' -H 'Content-Type: application/json' -H "X_API_KEY: food"

# textile product
curl localhost:5000/products -d '{"name": "Baggy Jeans", "tags": ["baggy", "modern"], "colour": "maroon", "range": "jeans", "billOfMaterials": {"cloth": {"quantity": 10, "units": "runnning metres"}, "string": {"quantity": 12, "units": "metres"}}}' -H 'Content-Type: application/json' -H "X_API_KEY: textiles"

```

## Test reading the api
```bash
curl localhost:5000/products -H 'Content-Type: application/json' -H "X_API_KEY: food"
curl localhost:5000/products -H 'Content-Type: application/json' -H "X_API_KEY: textiles"
```

## Check lint issues
Note: pep8 is followed but line length is 120.
```bash
flake8
```

## Testing
```bash
pytest
```

## Adding new factories
The config file to set up new industries is called system_config.py.
The app is now flexible enough to accept a new type of product as long as we follow the basic setup:
1. In system_config.py
- Add new api key for the new industry.
- Add new api key to INDUSTRY_KEYS list.
- Add any new field names to product field keys
- Add corresponding singular table key names in TABLE_NAMES (these you will use to map objects to correct tables)
- PRODUCT_CONFIG dictionary is where you configure your product.
- Most likely you new product will belong to some collection (range, group, selection etc.) which we want to save as 
group in the database (so that they all have one system name) - add appropriate collection name to PRODUCT_GROUP in
PRODUCT_CONFIG dictionary.

2. PRODUCT_CONFIG
This is where you configure your new product ones all the new keys have been named etc.
- Each factory has its own config sub-dictionary with a key corresponding to the industry name (i.e: 'food', 'textiles')
- Remember to add your new industry above the file in INDUSTRY_KEYS!

## PRODUCT_CONFIG keys usage
- ALL_FIELDS - all json fields (not the system fields) that a properly specified product data should have. When sending json to the app this will be 
checked first
- BASE_FIELDS - all fields that we can instantiate the product object with as the base for adding relations to it. 
I.e once we have the Group and Customer created we can create a FoodProduct(name=name, group=group, customer=customer) 
- INDEPENDENT - fields for which we can create objects before having the product object.
- SINGLE_RELATIONS - fields which are a single object relation to the product (i.e. product is in one group, has one 
customer etc.)
- PRODUCT_DEPENDENT - fields which require product object to exist prior to adding the relation backwards to it. 
(i.e material requires product_id to properly save)
- PRODUCT_GROUP - original json field name for the group in this industry (i.e. for food we have family, textiles - 
range)
- MULTI_RELATIONS - fields describing product relations which will be linking multiple objects to the product (i.e. m2m)

## Adding models
After all is configured we need to add models. Add those that are not already defined in models.py.