from fastapi import FastAPI
from pydantic import BaseModel
import csv
import pika
import json

app = FastAPI()

class Prediction(BaseModel):
    image_frame: str
    prob: float
    tags: list[str]

class Data(BaseModel):
    license_id: str
    preds: list[Prediction]

class Payload(BaseModel):
    device_id: str
    client_id: str
    created_at: str
    data: Data

def push_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='predictions')
    channel.basic_publish(exchange='', routing_key='predictions', body=json.dumps(message))
    connection.close()


@app.post("/process")
async def process_data(payload: Payload):
    push_to_queue(payload.dict())

    return {'message': 'Data saved successfully'}

