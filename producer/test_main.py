# TABLE OF CONTENTS
# 1. Imports
# 2. Initialize TestClient
# 3. Test
# test_process_data
# test_1000_send_requests
# test_process_data_error
# 4. Function
# generate_random_string
# generate_random_request
# retrieve_data

# 1. Imports
from fastapi.testclient import TestClient
import json
import random
import string
from datetime import datetime
from .main import app

# 2. Initialize TestClient
client = TestClient(app)

# 3. Test
# test_process_data
def test_process_data():
    payload = {
        "device_id": "test_device",
        "client_id": "test_client",
        "created_at": "2023-05-14T12:00:00Z",
        "data": {
            "license_id": "test_license",
            "preds": [
                {
                    "image_frame": "image1.jpg",
                    "prob": 0.20,
                    "tags": ["cat", "animal"]
                },
                {
                    "image_frame": "image2.jpg",
                    "prob": 0.6,
                    "tags": ["dog", "animal"]
                }
            ]
        }
    }

    response = client.post("/process", json=payload)

    assert response.status_code == 200
    assert response.json() == payload

# test_1000_send_requests
def test_1000_send_requests():
    total_count = 0
    for i in range(1000):
        request_data = generate_random_request(i)
        total_count += len(request_data["data"]["preds"])
        headers = {'Content-Type': 'application/json'}
        response = client.post("/process", data=json.dumps(request_data), headers=headers)
        assert response.json() == request_data
    print(total_count)
    assert retrieve_data() == total_count + 2

# test_process_data_error
def test_process_data_error():
    payload = {}  # Invalid payload

    response = client.post("/process", json=payload)

    assert response.status_code == 422

# 4. Function
# generate_random_string
def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# generate_random_request
def generate_random_request(count):

    # Generate random data for the request body
    request_data = {
        'device_id': generate_random_string(10),
        'client_id': generate_random_string(10),
        'created_at': datetime.now().isoformat(),
        "data": {
            "license_id": "license_id",
            "preds": []
        }
    }
    # Generate random predictions
    preds_per_message = random.randint(1, 10)
    for i in range(preds_per_message):
        prediction = {
            "image_frame": f"image_frame_{i}_{count}",
            "prob": random.uniform(0, 1),
            "tags": []
        }
        request_data["data"]["preds"].append(prediction)
        
    return request_data

# retrieve_data
def retrieve_data():
    with open('./data/data.csv', 'r') as file:
        lines = file.readlines()
        return len(lines) - 1