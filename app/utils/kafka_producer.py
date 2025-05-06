from confluent_kafka import Producer
import json
import os

def get_kafka_producer():
    config = {
        'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    }
    return Producer(config)

def publish_email_event(event_type: str, data: dict):
    topic = f"email.{event_type}"
    producer = get_kafka_producer()
    producer.produce(topic, value=json.dumps(data).encode('utf-8'))
    producer.flush()
