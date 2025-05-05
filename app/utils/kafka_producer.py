from kafka import KafkaProducer
import json
import os

_producer = None
def get_kafka_producer():
    """Lazily initialize and return the KafkaProducer instance."""
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(","),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return _producer

def publish_email_event(event_type: str, data: dict):
    topic = f"email.{event_type}"
    producer = get_kafka_producer()
    producer.send(topic, value=data)
    producer.flush()
