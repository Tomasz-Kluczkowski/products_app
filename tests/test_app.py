import json

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


class TestAPICommon:

    def test_unknown_api_key(self, client):
        response = client.post(
            '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'skeleton_key'}
        )
        assert response.status_code == 403
        assert response.data == b'Unknown API key. Please check your API key.'

    def test_no_json(self, client):
        response = client.post(
            '/products', json=None, content_type='application/json', headers={'x_api_key': 'food'}
        )
        assert response.status_code == 400
        assert response.data == b'No JSON body supplied'

    def test_retrieve_unknown_product(self, client):
        response = client.get(
            '/products', content_type='application/json', headers={'x_api_key': 'skeleton_key'}
        )
        assert response.status_code == 403
        assert response.data == b'Unknown API key. Please check your API key.'


class TestFoodProducts:

    def test_add_food_product(self, client):
        response = client.post(
            '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'}
        )
        assert response.status_code == 201
        assert response.data == b'Product created'

    def test_duplicated_food_product_rejected(self, client):
        client.post('/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'})
        response = client.post(
            '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'}
        )
        assert response.status_code == 400
        assert response.data == b'Product already in database, use PUT or PATCH methods to amend.'

    def test_retrieve_food_product(self, client):
        client.post(
            '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'}
        )
        response = client.get(
            '/products', json=test_food_data, content_type='application/json', headers={'x_api_key': 'food'}
        )
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data == [
            {
                'allergens': [{'id': 1, 'name': 'cereals'}],
                'customer': {'id': 1, 'name': 'Deans Butchers'},
                'customer_id': 1,
                'group': {'id': 1, 'name': 'sausage'},
                'group_id': 1,
                'id': 1,
                'materials': [
                    {'id': 1, 'name': 'paprika', 'product_id': 1, 'quantity': 100.0, 'units': 'tablespoons'},
                    {'id': 2, 'name': 'pork mince', 'product_id': 1, 'quantity': 10.0, 'units': 'kg'}
                ],
                'name': 'Chorizo',
                'tags': [
                    {'id': 1, 'name': 'spicy'},
                    {'id': 2, 'name': 'spanish'}
                ],
                'type': 'food_product'}
        ]


class TestTextileProducts:
    def test_add_textile_product(self, client):
        response = client.post(
            '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
        )
        assert response.status_code == 201
        assert response.data == b'Product created'

    def test_duplicated_textile_product_rejected(self, client):
        client.post(
            '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
        )
        response = client.post(
            '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
        )
        assert response.status_code == 400
        assert response.data == b'Product already in database, use PUT or PATCH methods to amend.'

    def test_retrieve_textile_product(self, client):
        client.post(
            '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
        )
        response = client.get(
            '/products', json=test_textile_data, content_type='application/json', headers={'x_api_key': 'textile'}
        )
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data == [
            {
                'colour': 'Maroon',
                'group': {'id': 1, 'name': 'Grandad Chic'},
                'group_id': 1,
                'id': 1,
                'materials': [
                    {'id': 1, 'name': 'Maroon wool', 'product_id': 1, 'quantity': 100.0, 'units': 'metres'},
                    {'id': 2, 'name': 'Silk lining', 'product_id': 1, 'quantity': 10.0, 'units': 'square metres'}
                ],
                'name': 'Tweed Jacket',
                'tags': [
                    {'id': 1, 'name': 'mens'},
                    {'id': 2, 'name': 'smart'},
                    {'id': 3, 'name': 'suits'}
                ],
                'type': 'textile_product'}
        ]
