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


def test_add_food_product(recreate_database):

    with app.test_client() as c:
        response = c.post(
            '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'}
        )
        assert response.status_code == 201
        assert response.data == b'Product created'


def test_add_textile_product(recreate_database):
    with app.test_client() as c:
        response = c.post(
            '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
        )
        assert response.status_code == 201
        assert response.data == b'Product created'
