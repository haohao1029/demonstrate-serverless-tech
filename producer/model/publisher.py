import pika
import os
import json
import logging

class Publisher:
    def __init__(self, queue, exchange) -> None:
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBITMQ_HOST", 'localhost')))
        self.queue = queue
        self.exchange = exchange
        self.connect()
        
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBITMQ_HOST", 'localhost')))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='predictions')

    def _publish(self, message):
        self.channel.basic_publish(exchange='', routing_key='predictions', body=json.dumps(message))
        logging.info(f"Message published to the queue: {message}")
    
    def publish(self, message):
        try:
            self._publish(message)
        except pika.exceptions.StreamLostError as e:
            logging.error(f"Failed to publish message to the queue: {str(e)}")
            logging.debug('reconnecting to queue')
            self.connect()
            self._publish(message)
