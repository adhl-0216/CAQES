from datetime import datetime
import json
import nats
from models import AlertJob


class AlertParser:
    def __init__(self):
        self.nc = None
        self.js = None

    async def connect(self):
        self.nc = await nats.connect("nats://nats:4222")
        self.js = self.nc.jetstream()

    async def start_worker(self):
        await self.connect()

        async def process_job(msg):
            try:
                job_data = json.loads(msg.data.decode())
                job = AlertJob.model_validate(job_data)

                # Process the alert
                # Your alert processing logic here

                job.status = "completed"
                job.processed_at = datetime.utcnow()

                # Acknowledge the message
                await msg.ack()

            except Exception as e:
                print(f"Error processing job: {e}")
                # Negative acknowledge to retry
                await msg.nak()

        # Create durable consumer for work queue
        await self.js.subscribe(
            "alerts.jobs",
            durable="alert-parser-group",
            cb=process_job,
            flow_control=True,
            manual_ack=True
        )
