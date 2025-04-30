from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'kafka:9092'})

def publish_email_event(event_type: str, data: dict):
    topic = f"email.{event_type}"
    producer.produce(topic, value=json.dumps(data).encode('utf-8'))
    producer.flush()
