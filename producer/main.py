# TABLE OF CONTENTS
# 1. Imports
# 2. Initialze FastAPI and RabbitMQ connection
# 3. Function 
# push_to_queue
# 4. Route 
# process_data

# 1. Imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, BaseSettings
import csv
import pika
import json
import logging
import os
from model.payload import Payload
from model.publisher import Publisher


# 2. Initialze FastAPI and RabbitMQ connection
app = FastAPI()
publisher = Publisher('predictions', '')

# 3. Function
# push_to_queue
def push_to_queue(message):
    try:
        publisher.publish(message)
    except Exception as e:
        logging.error(f"Failed to push message to the queue: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to push message to the queue")

# 4. Route
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