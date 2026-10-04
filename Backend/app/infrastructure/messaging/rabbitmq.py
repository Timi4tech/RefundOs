import json
from typing import Any, Awaitable, Callable
from uuid import uuid4
import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import AbstractIncomingMessage
from app.core.config import settings


class RabbitMQClient:
    EXCHANGE_NAME = "banking.events"
    REFUND_QUEUE = "refund.processing"
    REFUND_ROUTING_KEY = "refund.requested"
    DLX = "banking.dead_letter"
    DLQ = "refund.dead_letter"

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.refund_queue = None
        self.response_queue = None
        self.response_routing_key = None

    async def connect(self):
        if self.connection and not self.connection.is_closed:
            return
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        self.exchange = await self.channel.declare_exchange(self.EXCHANGE_NAME, ExchangeType.TOPIC, durable=True)
        dlx = await self.channel.declare_exchange(self.DLX, ExchangeType.TOPIC, durable=True)
        dlq = await self.channel.declare_queue(self.DLQ, durable=True)
        await dlq.bind(dlx, routing_key="refund.failed")
        self.refund_queue = await self.channel.declare_queue(
            self.REFUND_QUEUE,
            durable=True,
            arguments={"x-dead-letter-exchange": self.DLX, "x-dead-letter-routing-key": "refund.failed"},
        )
        await self.refund_queue.bind(self.exchange, routing_key=self.REFUND_ROUTING_KEY)

    async def start_response_listener(self, callback: Callable[[AbstractIncomingMessage], Awaitable[None]]) -> None:
        if self.channel is None or self.exchange is None:
            raise RuntimeError("RabbitMQ is not connected.")
        self.response_routing_key = f"refund.response.{uuid4()}"
        self.response_queue = await self.channel.declare_queue(
            name="",
            durable=False,
            exclusive=True,
            auto_delete=True,
        )
        await self.response_queue.bind(self.exchange, routing_key=self.response_routing_key)
        await self.response_queue.consume(callback, no_ack=False)

    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        if self.exchange is None:
            raise RuntimeError("RabbitMQ is not connected.")
        await self.exchange.publish(
            Message(
                body=json.dumps(payload, default=str).encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )

    async def publish_refund_request(self, payload: dict[str, Any]) -> None:
        if not self.response_routing_key:
            raise RuntimeError("Refund response listener has not been started.")
        event = {**payload, "reply_to": self.response_routing_key}
        await self.publish(self.REFUND_ROUTING_KEY, event)

    async def publish_refund_decision(self, reply_to: str, payload: dict[str, Any]) -> None:
        await self.publish(reply_to, payload)

    async def consume(self, callback: Callable[[AbstractIncomingMessage], Awaitable[None]]):
        if self.refund_queue is None:
            raise RuntimeError("RabbitMQ is not connected.")
        await self.refund_queue.consume(callback, no_ack=False)

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
        self.connection = None
        self.channel = None
        self.exchange = None
        self.refund_queue = None
        self.response_queue = None
        self.response_routing_key = None


rabbitmq_client = RabbitMQClient()
