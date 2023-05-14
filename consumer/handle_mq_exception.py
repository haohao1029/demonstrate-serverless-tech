import asyncio

async def retry_message(message, retry_count):
    # Retry the message after a delay
    retry_count += 1
    retry_delay = 0.5  # Delay in seconds before retrying
    print(f"Retrying message ({retry_count} attempt) in {retry_delay} seconds...")
    await asyncio.sleep(retry_delay)
    
    # add retry_count to message properties
    properties = message.properties
    properties.headers['retry_count'] = retry_count
     
    # Requeue: Publish the message to the same queue
    await message.channel.basic_publish(
        exchange='',
        routing_key=message.routing_key,
        body=message.body,
        properties= properties,
    )


async def push_to_dead_letter_queue(message):
    exchange_name = 'dead_letter'
    queue_name = 'dead_letter_queue'
    routing_key = 'dead_letter'
    dead_letter_args = {
    "x-dead-letter-exchange": exchange_name,
    "x-dead-letter-routing-key": routing_key
    }

    await message.channel.exchange_declare(
        exchange='dlx_exchange',
    )
    await message.channel.queue_declare(
        queue='dead_letter_queue',
        durable=True,
        auto_delete=False,
        arguments={"x-dead-letter-exchange": "dlx_exchange",
              "x-dead-letter-routing-key": "dlx_key"}
    )
    # bind the queue to the exchange
    await message.channel.queue_bind(
        queue='dead_letter_queue',
        exchange='dlx_exchange',
        routing_key='dlx_key',
    )
    properties = message.properties
    message.properties.headers['x-delay'] = 2500
    await message.channel.basic_publish(
        body=message.body,
        exchange='dlx_exchange',
        routing_key='dead_letter',
        properties=properties
    )