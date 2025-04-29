from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_email_event(event_type: str, data: dict):
    topic = f"email.{event_type}"
    producer.send(topic, value=data)
    producer.flush()
