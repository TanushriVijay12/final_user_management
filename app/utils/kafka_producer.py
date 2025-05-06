from confluent_kafka import Producer
import json
import os

_producer = None

def get_kafka_producer():
    """Lazily initialize and return the Confluent Kafka Producer instance."""
    global _producer
    if _producer is None:
        _producer = Producer({
            'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        })
    return _producer

def delivery_report(err, msg):
    """Callback to confirm message delivery or report error."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_email_event(event_type: str, data: dict):
    topic = f"email.{event_type}"
    producer = get_kafka_producer()
    value = json.dumps(data).encode("utf-8")
    
    # Send with delivery callback
    producer.produce(topic, value=value, callback=delivery_report)
    producer.flush()
