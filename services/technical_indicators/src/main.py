from loguru import logger
from quixstreams import Application


def run(
    # kafka parameters
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_consumer_group: str,
    # candles parameters
    candle_seconds: int,
):
    """
    Transforms a stream of input candles into a stream of technical indicators.

    In 3 steps:
    - Ingests candles from the `kafka_input_topic`
    - Computes technical indicators
    - Produces technical indicators to the `kafka_output_topic`

    Args:
        kafka_broker_address (str): Kafka broker address
        kafka_input_topic (str): Kafka input topic name
        kafka_output_topic (str): Kafka output topic name
        kafka_consumer_group (str): Kafka consumer group name
        candle_seconds (int): Candle duration in seconds

    Returns:
        None
    """
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
    )

    # input topic
    candles_topic = app.topic(kafka_input_topic, value_deserializer='json')
    # output topic
    technical_indicators_topic = app.topic(kafka_output_topic, value_serializer='json')

    # Step 1. Ingest candles from the input kafka topic
    # Create a Streaming DataFrame connected to the input Kafka topic
    sdf = app.dataframe(topic=candles_topic)

    # Keep only the candles for the given `candle_seconds`
    sdf = sdf[sdf['candle_seconds'] == candle_seconds]

    # Step 2. Compute technical indicators from candles
    # TODO: data processsing here

    # logging on the console
    sdf = sdf.update(lambda value: logger.debug(f'Final message: {value}'))

    # Step 3. Produce the candles to the output kafka topic
    sdf = sdf.to_topic(technical_indicators_topic)

    # Starts the streaming app
    app.run()


if __name__ == '__main__':
    from technical_indicators.config import config

    # breakpoint()
    run(
        kafka_broker_address=config.kafka_broker_address,
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_consumer_group=config.kafka_consumer_group,
        candle_seconds=config.candle_seconds,
    )