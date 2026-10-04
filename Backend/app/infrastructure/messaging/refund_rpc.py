import asyncio
import json
from typing import Any
from aio_pika.abc import AbstractIncomingMessage
from app.infrastructure.messaging.rabbitmq import rabbitmq_client

_pending: dict[str, asyncio.Future[dict[str, Any]]] = {}


async def start_refund_response_listener() -> None:
    await rabbitmq_client.start_response_listener(handle_refund_response)


async def handle_refund_response(message: AbstractIncomingMessage) -> None:
    try:
        payload = json.loads(message.body.decode("utf-8"))
        correlation_id = payload.get("request_id")
        future = _pending.get(correlation_id)
        if future and not future.done():
            future.set_result(payload)
        await message.ack()
    except Exception:
        await message.reject(requeue=False)


async def request_refund(payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    request_id = str(payload["request_id"])
    loop = asyncio.get_running_loop()
    future: asyncio.Future[dict[str, Any]] = loop.create_future()
    _pending[request_id] = future
    try:
        await rabbitmq_client.publish_refund_request(payload)
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        _pending.pop(request_id, None)
