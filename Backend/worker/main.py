import asyncio
from app.infrastructure.database import connect_db, disconnect_db
from app.infrastructure.messaging.rabbitmq import rabbitmq_client
from app.infrastructure.messaging.refund_consumer import RefundConsumer

async def main():
    await connect_db(); consumer=RefundConsumer(); await consumer.start()
    try: await asyncio.Future()
    finally:
        await rabbitmq_client.close(); await disconnect_db()

if __name__=="__main__": asyncio.run(main())
