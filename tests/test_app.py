import pytest

from app import app

test_food_data = {
    "name": "Chorizo",
    "family": "sausage",
    "tags": [
        "spicy",
        "spanish"
    ],
    "allergens": [
        "cereals"
    ],
    "customer": "Deans Butchers",
    "billOfMaterials": {
        "paprika": {
            "quantity": 100,
            "units": "tablespoons"
        },
        "pork mince": {
            "quantity": 10,
            "units": "kg"
        }
    }
}

test_textile_data = {
    "name": "Tweed Jacket",
    "colour": "Maroon",
    "range": "Grandad Chic",
    "tags": [
        "mens",
        "smart",
        "suits"
    ],
    "billOfMaterials": {
        "Maroon wool": {
            "quantity": 100,
            "units": "metres"
        },
        "Silk lining": {
            "quantity": 10,
            "units": "square metres"
        }
    }
}


@pytest.mark.usefixtures("recreate_database")
class TestAPICommon:

    def test_unknown_api_key(self):
        with app.test_client() as c:
            response = c.post(
                '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'skeleton_key'}
            )
            assert response.status_code == 403
            assert response.data == b'Unknown API key. Please check your API key.'

    def test_no_json(self):
        with app.test_client() as c:
            response = c.post(
                '/products', json=None, content_type='application/json', headers={'x_api_key': 'food'}
            )
            assert response.status_code == 400
            assert response.data == b'No JSON body supplied'

    def test_retrieve_unknown_product(self):
        with app.test_client() as c:
            response = c.get(
                '/products', content_type='application/json', headers={'x_api_key': 'skeleton_key'}
            )
            assert response.status_code == 403
            assert response.data == b'Unknown API key. Please check your API key.'


@pytest.mark.usefixtures("recreate_database")
class TestFoodProducts:

    def test_add_food_product(self):

        with app.test_client() as c:
            response = c.post(
                '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'}
            )
            assert response.status_code == 201
            assert response.data == b'Product created'

    def test_duplicated_food_product_rejected(self):

        with app.test_client() as c:
            c.post('/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'})
            response = c.post(
                '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'}
            )
            assert response.status_code == 400
            assert response.data == b'Product already in database, use PUT or PATCH methods to amend.'


@pytest.mark.usefixtures("recreate_database")
class TestTextileProducts:
    def test_add_textile_product(self):
        with app.test_client() as c:
            response = c.post(
                '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
            )
            assert response.status_code == 201
            assert response.data == b'Product created'

    def test_duplicated_textile_product_rejected(self):

        with app.test_client() as c:
            c.post(
                '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
            )
            response = c.post(
                '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
            )
            assert response.status_code == 400
            assert response.data == b'Product already in database, use PUT or PATCH methods to amend.'

