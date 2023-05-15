# TABLE OF CONTENTS
# 1. Imports
# 2. Initialize variables and Lock
# 3. Function
# save message data to csv
# 4. Callback Preprocessing
# 5. Main consume_queue

# 1. Imports
import asyncio
import aio_pika
import csv
import json
import os
from handle_mq_exception import retry_message, push_to_dead_letter_queue 

# 2. Initialize variables and Lock
csv_path = './data/data.csv'
lock = asyncio.Lock()
queue_name = 'predictions'

# 3. Function
# save message data to csv
def save_to_csv(data):
    with open(csv_path, 'a+', newline='') as file:
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
            
# 4. Callback Preprocessing 
async def callback(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    try:
        print(" [x] Received %r" % message.body)
        data = json.loads(message.body)
        async with lock:
            for prediction in data['data']['preds']:
                if prediction["prob"] < 0.25:
                    prediction['tags'].append('low_prob')
            save_to_csv(data)
    except Exception as e:
        retry_count = message.headers.get('retry_count', 0)
        print(message.info())
        if retry_count < 3:
            await retry_message(message, retry_count)
        else:
            # Dead-letter the message
            print("Rejecting message...")
            await push_to_dead_letter_queue(message)
            print("Message moved to dead letter queue:", message.body)
    finally:
        await message.ack()



# 5. Main consume_queue
async def consume_queue():
    connection = await aio_pika.connect_robust(
         "amqp://guest:guest@" + os.getenv("RABBITMQ_HOST", 'localhost')
    )
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, auto_delete=False)
    await queue.consume(callback)

    print('Waiting for messages. To exit, press CTRL+C')
    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await connection.close()

if __name__ == "__main__":
    if os.path.isfile(csv_path) == False:
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(['device_id', 'client_id', 'created_at', 'license_id', 'image_frame', 'prob', 'tags'])    
    asyncio.run(consume_queue())
