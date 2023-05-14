# TABLE OF CONTENTS
# 1. Imports
# 2. Initialze FastAPI and RabbitMQ connection
# 3. Data Model
# Predictions
# Data
# Payload
# 4. Function 
# push_to_queue
# 5. Route 
# process_data

# 1. Imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, BaseSettings
import csv
import pika
import json
import logging
import os

# Initialze FastAPI and RabbitMQ connection
app = FastAPI()


# 3. Data Model
# Predictions
class Prediction(BaseModel):
    image_frame: str
    prob: float
    tags: list[str]

# Data
class Data(BaseModel):
    license_id: str
    preds: list[Prediction]

# Payload
class Payload(BaseModel):
    device_id: str
    client_id: str
    created_at: str
    data: Data


# 4. Function
# push_to_queue
def push_to_queue(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBITMQ_HOST", 'localhost')))
        channel = connection.channel()
        channel.queue_declare(queue='predictions')
        channel.basic_publish(exchange='', routing_key='predictions', body=json.dumps(message))
        channel.close()
    except Exception as e:
        logging.error(f"Failed to push message to the queue: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to push message to the queue")

# 5. Route
# process_data
@app.post("/process")
async def process_data(payload: Payload):
    try:
        push_to_queue(payload.dict())
        return payload
    except HTTPException:
        raise  # Re-raise the exception to let FastAPI handle it
    except Exception as e:
        logging.error(f"An error occurred while processing the request: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request")