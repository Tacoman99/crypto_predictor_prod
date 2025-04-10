# Create an Application instance with Kafka configs
from quixstreams import Application

# application handles all low level details to connect to kafka
app = Application(
    broker_address='localhost:31234', consumer_group='trades'
)

# Define a topic "my_topic" with JSON serialization, create connection to kafka topic and creates it if it doesn't exist
topic = app.topic(name='my_topic', value_serializer='json')

event = {"id": "1", "text": "Lorem ipsum dolor sit amet"}

# Create a Producer instance, object that pushes messages to kafka
with app.get_producer() as producer:

    while True:

        # 1) fetch data from external api
        event = {"id": "1", "text": "Lorem ipsum dolor sit amet"}

        # 2)Serialize an event using the defined Topic,  must serialize event since kafka is a binary protocol
        message = topic.serialize(key=event["id"], value=event)

        # 3) Produce a message into the Kafka topic, push message to kafka
        producer.produce(
            topic=topic.name, 
            value=message.value, 
            key=message.key # important when having modular systems
        )

        import time
        time.sleep(1)