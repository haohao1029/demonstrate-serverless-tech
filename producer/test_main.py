from fastapi.testclient import TestClient
import json
import random
import string
from datetime import datetime

from .main import app

client = TestClient(app)

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

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

def send_requests():
    total_count = 0
    for i in range(1000):
        request_data = generate_random_request(i)
        total_count += len(request_data["data"]["preds"])
        headers = {'Content-Type': 'application/json'}
        response = client.post("/process", data=json.dumps(request_data), headers=headers)
        assert response.json() == request_data
    print(total_count)
    assert retrieve_data() == total_count
    
def retrieve_data():
    with open('./data/data.csv', 'r') as file:
        lines = file.readlines()
        return len(lines) - 1

def test_main():
    send_requests()

if __name__ == "__main__":
    test_main()
