import asyncio
import aio_pika
import csv
import json
import os

lock = asyncio.Lock()

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

async def callback(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process():
        try:
            print(" [x] Received %r" % message.body)
            data = json.loads(message.body)
            async with lock:
                for prediction in data['data']['preds']:
                    if prediction["prob"] < 0.25:
                        prediction['tags'].append('low_prob')
                save_to_csv(data)
                message.ack()
        except Exception as e:
            print(e)
            if message.delivery_tag < 5:
                # log the message
                message.nack(requeue=True)
                print(f"Requeueing message: {data}")
            else:
                message.reject()

async def consume_queue():
    connection = await aio_pika.connect_robust(
         "amqp://guest:guest@" + os.getenv("RABBITMQ_HOST", 'localhost')
    )
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=100)
    queue = await channel.declare_queue('predictions', auto_delete=False)
    await queue.consume(callback)

    print('Waiting for messages. To exit, press CTRL+C')
    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await connection.close()

if __name__ == "__main__":
    if os.path.isfile('data.csv') == False:
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(['device_id', 'client_id', 'created_at', 'license_id', 'image_frame', 'prob', 'tags'])    

    asyncio.run(consume_queue())
