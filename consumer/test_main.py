import pytest
import asyncio
import aio_pika
import os
import csv
import json
from unittest.mock import MagicMock
import random
import string
from datetime import datetime
from main import callback, save_to_csv

csv_path = os.getenv('CSV_PATH', './data/test_data.csv')
with open(csv_path, 'w', newline='') as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerow(['device_id', 'client_id', 'created_at', 'license_id', 'image_frame', 'prob', 'tags'])    

@pytest.fixture
def message():
    message = MagicMock(spec=aio_pika.IncomingMessage)
    message.body = json.dumps({
        'device_id': '123',
        'client_id': '456',
        'created_at': '2023-05-15',
        'data': {
            'preds': [
                {
                    'image_frame': 'frame1',
                    'prob': 0.3,
                    'tags': []
                },
                {
                    'image_frame': 'frame2',
                    'prob': 0.2,
                    'tags': []
                }
            ],
            'license_id': '789'
        }
    }).encode('utf-8')
    return message

def test_save_to_csv(message):
    data = json.loads(message.body)
    save_to_csv(data)
    assert os.path.isfile(csv_path)

    with open(csv_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)

    assert len(rows) == 3  # Header + 2 rows
    assert rows[1][0] == '123'  # device_id
    assert rows[1][1] == '456'  # client_id
    assert rows[1][2] == '2023-05-15'  # created_at
    assert rows[1][3] == '789'  # license_id
    assert rows[1][4] == 'frame1'  # image_frame
    assert rows[1][5] == '0.3'  # prob

    assert rows[2][0] == '123'  # device_id
    assert rows[2][1] == '456'  # client_id
    assert rows[2][2] == '2023-05-15'  # created_at
    assert rows[2][3] == '789'  # license_id
    assert rows[2][4] == 'frame2'  # image_frame
    assert rows[2][5] == '0.2'  # prob

def test_callback(message):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(callback(message))

    assert os.path.isfile(csv_path)

    with open(csv_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)

    assert len(rows) == 5  # Header + 2 rows
    assert rows[3][0] == '123'  # device_id
    assert rows[3][1] == '456'  # client_id
    assert rows[3][2] == '2023-05-15'  # created_at
    assert rows[3][3] == '789'  # license_id
    assert rows[3][4] == 'frame1'  # image_frame
    assert rows[3][5] == '0.3'  # prob
    assert rows[4][6] == 'low_prob'  # prob

# 1000 random requests
def test_callback_random():
    message = MagicMock(spec=aio_pika.IncomingMessage)
    total_rows = 0
    for i in range(1000):
        request_data = generate_random_request(i)
        message.body = json.dumps(request_data).encode('utf-8')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(callback(message))
        total_rows += len(request_data['data']['preds'])
    with open(csv_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)
        assert len(rows) == total_rows + 5
        
# generate_random_string
def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# generate_random_request
def generate_random_request(count):
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
