from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import pika
import json
import logging

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
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='predictions')
        channel.basic_publish(exchange='', routing_key='predictions', body=json.dumps(message))
        connection.close()
    except Exception as e:
        logging.error(f"Failed to push message to the queue: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to push message to the queue")




@app.post("/process")
async def process_data(payload: Payload):
    try:
        push_to_queue(payload.dict())
        return {'message': 'Data saved successfully'}
    except HTTPException:
        raise  # Re-raise the exception to let FastAPI handle it
    except Exception as e:
        logging.error(f"An error occurred while processing the request: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request")

