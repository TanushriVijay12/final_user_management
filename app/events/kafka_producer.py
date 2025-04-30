# app/events/kafka_producer.py
from kafka import KafkaProducer
import json
import logging

logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_event(topic: str, event: dict):
    try:
        logger.info(f"Sending event to topic {topic}: {event}")
        producer.send(topic, event)
        producer.flush()
    except Exception as e:
        logger.error(f"Failed to send event to Kafka: {str(e)}")
