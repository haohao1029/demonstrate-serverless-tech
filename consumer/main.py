import pika
import csv
import json
import os

def save_to_csv(data):
    with open('data.csv', 'a+', newline='') as file:
        writer = csv.writer(file, delimiter=";")
        for prediction in data['data']['preds']:
            tags = ','.join(prediction['tags'])
            row = [
                data['device_id'],
                data['client_id'],
                data['created_at'],
                data['data']['license_id'],
                prediction['image_frame'],
                prediction['prob'],
                tags
            ]
            writer.writerow(row)


def callback(ch, method, properties, body):
    message = json.loads(body)
    for prediction in message['data']['preds']:
        if prediction["prob"] < 0.25:
            prediction['tags'].append('low_prob')
    save_to_csv(message)
    print(f"Received message: {message}")


def consume_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBITMQ_HOST", 'localhost')))
    channel = connection.channel()
    channel.queue_declare(queue='predictions')
    channel.basic_consume(queue='predictions', on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()

# if 'data.csv' does not exist, create it and add the header row
if os.path.isfile('data.csv') == False:
    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(['device_id', 'client_id', 'created_at', 'license_id', 'image_frame', 'prob', 'tags'])    
    

consume_queue()
