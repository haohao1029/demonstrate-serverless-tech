# tapway-interview

## How To Run
``` bash
docker-compose up --build
```
## Project Structure
``` bash
tapway-interview
├─ consumer
│  ├─ Dockerfile
│  ├─ main.py
│  ├─ Pipfile
│  ├─ Pipfile.lock
│  └─ requirements.txt
├─ docker-compose.yml
├─ producer
│  ├─ Dockerfile
│  ├─ main.py
│  ├─ Pipfile
│  ├─ Pipfile.lock
│  ├─ requirements.txt
│  ├─ test_main.py
│  └─ __init__.py
└─ README.md

```

## Project Images
With the docker-compose up --build, rabbimq will be started. producer, consumer and tests will be start only after rabbimq's status become `service-healthy`.

### RabbitMQ 
rabbitmq:3-management-alpine was pulled and started

### Producer 
Producer have a `/process` POST API to publish message into RabbitMQ, the API will instance return status code 200 once the message is publish to the RabbitMQ. With this method we risk losing the message if the consumer fails or crashes before processing it.

### Consumer 
Consumer subscribed to rabbitmq channel, preprocess it and append it into csv file. The delimiter used for csv is ";" because "tags" column is using "," to seperate multiple tags

### Tests
Tests container will run the `test_main.py` file in producer by using `pytest`. It will call 1,000 APIs with `1~10 preds per API call` to producer API and producer message into RabbitMQ.

