# app/events/kafka_producer.py
from confluent_kafka import Producer
import json
import logging

logger = logging.getLogger(__name__)

# Correct config key: 'bootstrap.servers' (with a dot)
producer = Producer({
    'bootstrap.servers': 'kafka:9092'
})

def send_event(topic: str, event: dict):
    try:
        serialized_event = json.dumps(event).encode('utf-8')
        producer.produce(topic, value=serialized_event)
        producer.flush()
        logger.info(f"✅ Event sent to topic `{topic}`: {event}")
    except Exception as e:
        logger.error(f"❌ Failed to send event to Kafka topic `{topic}`: {e}")
