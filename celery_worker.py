from celery import Celery
from confluent_kafka import Consumer
import json
import threading
import os
from app.tasks.email_tasks import send_email_task

# Celery config
app = Celery(
    "celery_worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

# Kafka config
KAFKA_TOPICS = [
    "email.account.verification",
    "email.account.lock",
    "email.account.unlock",
    "email.role.upgrade",
    "email.status.professional"
]

def kafka_event_listener():
    consumer = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'email-group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(KAFKA_TOPICS)
    print("✅ Kafka consumer started, waiting for messages...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue
        print(f"📩 Kafka msg on `{msg.topic()}`: {msg.value().decode('utf-8')}")
        payload = json.loads(msg.value())
        payload["event"] = msg.topic().replace("email.", "")
        send_email_task.delay(payload)

# ✅ Only run consumer in standalone script mode
if __name__ == "__main__":
    threading.Thread(target=kafka_event_listener, daemon=True).start()
