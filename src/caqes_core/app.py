import asyncio
from alerts.alert_parser import AlertParser
from alerts.alert_listener import AlertListener


class CaqesApplication:
    def __init__(self):
        self.listener = AlertListener()
        self.parsers = []
        self.num_workers = 3

    async def start(self):
        # Start the alert listener
        await self.listener.connect()
        listener_task = asyncio.create_task(self.listener.subscribe())

        # Start multiple parser workers
        parser_tasks = []
        for _ in range(self.num_workers):
            parser = AlertParser()
            self.parsers.append(parser)
            parser_tasks.append(parser.start_worker())

        # Combine all tasks
        tasks = [listener_task] + parser_tasks

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error in application: {e}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        await self.listener.close()
        for parser in self.parsers:
            await parser.close()


def main():
    """Synchronous entry point that runs the async application"""
    app = CaqesApplication()
    asyncio.run(app.start())
