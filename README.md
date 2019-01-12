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
curl localhost:5000/products -d '{"name": "Chorizo", "tags": ["spicy", "spanish"], "customer": "Deans Butchers", "family": "sausage", "allergens": ["cereals"], "billOfMaterials": {"paprika": {"quantity": 100, "units": "tablespoons"}, "pork mince": {"quantity": 10, "units": "kg"}}}' -H 'Content-Type: application/json' -H "X_API_KEY: food"
```

## Test reading the api
```bash
curl localhost:5000/products -H 'Content-Type: application/json' -H "X_API_KEY: food"
```

## Check lint issues
Note: pep8 is followed but line length is 120.
```bash
flake8
```