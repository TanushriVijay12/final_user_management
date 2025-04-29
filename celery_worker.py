from celery import Celery

app = Celery(
    "email_tasks",
    broker="kafka://kafka:9092",  # Celery won't work directly with Kafka, we will patch this later
    backend="rpc://"
)

@app.task
def send_email_task(to_email: str, subject: str, body: str):
    print(f"Sending email to {to_email}: {subject} — {body}")
