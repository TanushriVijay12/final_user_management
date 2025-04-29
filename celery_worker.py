import json
import time
from kafka import KafkaConsumer
from celery import Celery
from app.services.email_service import EmailService

# Celery config
app = Celery("email_tasks", broker="redis://localhost:6379/0")  # We will correct this if needed

# Kafka Consumer Configuration
TOPICS = [
    "email.account.verification",
    "email.account.locked",
    "email.account.unlocked",
    "email.role.upgraded",
    "email.pro.upgraded"
]

consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='email-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

@app.task
def listen_and_dispatch():
    print("Listening for Kafka events...")
    while True:
        for message in consumer:
            try:
                print(f"Event Received on topic {message.topic}")
                data = message.value

                to_email = data.get("to")
                subject = data.get("subject")
                body = data.get("body")

                if not all([to_email, subject, body]):
                    print("Incomplete email data. Skipping...")
                    continue

                # 📨 Send email
                EmailService().send_email(to_email, subject, body)
                print(f"Email sent to {to_email}")
            except Exception as e:
                print(f"Error handling message: {e}")

        time.sleep(1)  # Prevent tight loop
