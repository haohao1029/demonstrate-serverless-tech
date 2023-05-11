import requests
import json
import random

def generate_random_request(count):

    # Generate random data for the request body
    request_data = {
        "device_id": f"device_{count}_id",
        "client_id": f"client_{count}_id",
        "created_at": "2023-02-07 14:56:49.386042",
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
    url = "http://localhost:8000/process"  # Assuming the producer is running inside the Docker network

    for i in range(1000):
        request_data = generate_random_request(i)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(request_data), headers=headers)
        print(f"Response: {response.json()}")

send_requests()
