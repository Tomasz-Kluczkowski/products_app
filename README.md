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
curl localhost:5000/products -d '{"name": "Baggy Jeans", "tags": ["baggy", "modern"], "colour": "maroon", "range": "jeans", "billOfMaterials": {"cloth": {"quantity": 10, "units": "runnning metres"}, "string": {"quantity": 12, "units": "metres"}}}' -H 'Content-Type: application/json' -H "X_API_KEY: textile"

```

## Test reading the api
```bash
curl localhost:5000/products -H 'Content-Type: application/json' -H "X_API_KEY: food"
curl localhost:5000/products -H 'Content-Type: application/json' -H "X_API_KEY: textile"
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
The app is now flexible enough to accept a new type of product as long as we follow the basic setup:
1. In app.py
- Add new api key for the new industry
- Add new api key to INDUSTRY_KEYS list
- Add any new field names to product field keys
- Add corresponding singular table key names (these you will use to map objects to correct tables)
- Most likely you new product will belong to some collection (range, group, selection etc.) which we want to save as 
group in the database - add appropriate collection name to PRODUCT_GROUPS.
- Add object group key if you need to create product specific objects in the database.
