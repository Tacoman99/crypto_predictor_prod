def risingwave_table(
    table_name: str,
    kafka_broker_address: str,
    kafka_topic: str,
):
    """
    Creates a table with a given name and a given schema, connecting to a kafka topic.
    RisingWave will automatically create the table in the database.
    """
    # table = Table(
    #     name="technical_indicators",
    #     schema=Schema(
    #         pair=String,
    #         open=Float)
