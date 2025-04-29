from celery import Celery
from kafka import KafkaConsumer
import json
import threading
import os
from app.services.email_service import EmailService
from app.tasks.email_tasks import send_email_task

# Celery configuration
celery_app = Celery(
    "celery_worker.app",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

# Kafka consumer config
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPICS = [
    "account_verification",
    "account_lock",
    "account_unlock",
    "role_upgrade",
    "status_upgrade"
]

def kafka_event_listener():
    """Background Kafka consumer thread."""
    consumer = KafkaConsumer(
        *KAFKA_TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="email-group"
    )

    print("✅ Kafka consumer started, waiting for messages...")

    for message in consumer:
        print(f"📩 Received Kafka message on topic `{message.topic}`: {message.value}")
        payload = message.value

        # Dispatch to Celery task
        send_email_task.delay(payload)

# Launch the Kafka consumer in a background thread when the worker starts
threading.Thread(target=kafka_event_listener, daemon=True).start()
