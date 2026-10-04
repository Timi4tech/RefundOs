from __future__ import annotations

import logging
from uuid import uuid4
from app.application.dto.ai_dto import RefundWorkerDecision, RefundWorkerRequest
from app.infrastructure.ai.gemini_service import GeminiUnavailable, gemini_service
from app.infrastructure.messaging.refund_rpc import request_refund
from app.core.config import settings

logger = logging.getLogger(__name__)

class RefundChatOrchestrator:
    async def handle(self, user_id: str, message: str, history: list[dict[str, str]] | None = None) -> str:
        try:
            intent = await gemini_service.extract_refund_intent(message, history)
        except GeminiUnavailable:
            logger.exception("Gemini call failed")
            return "The refund assistant is temporarily unavailable. Please try again shortly."

        if intent.intent == "refund_request":
            missing = list(intent.missing_fields)
            if not intent.transaction_id:
                missing.append("transaction_id") if "transaction_id" not in missing else None
            if not intent.reason:
                missing.append("reason") if "reason" not in missing else None
            if missing:
                return await gemini_service.general_response(
                    f"The extracted refund request is missing these required details: {', '.join(dict.fromkeys(missing))}. Ask the customer for the missing details only.",
                    history,
                )

            request_id = str(uuid4())
            request = RefundWorkerRequest(
                request_id=request_id,
                user_id=user_id,
                transaction_id=intent.transaction_id,
                amount=intent.amount,
                reason=intent.reason,
            )
            try:
                worker_result = await request_refund(
                    request.model_dump(mode="json"),
                    settings.REFUND_WORKER_TIMEOUT_SECONDS,
                )
                decision = RefundWorkerDecision.model_validate(worker_result)
                if decision.request_id != request_id:
                    raise ValueError("Refund worker response correlation mismatch.")
            except Exception:
                return "I received your refund request, but the refund processing service is temporarily unavailable. Please try again shortly."

            try:
                return await gemini_service.present_decision(message, decision, history)
            except GeminiUnavailable:
                return self._safe_decision_response(decision)

        try:
            return await gemini_service.general_response(message, history)
        except GeminiUnavailable:
            return "The support assistant is temporarily unavailable. Please try again shortly."

    @staticmethod
    def _safe_decision_response(decision: RefundWorkerDecision) -> str:
        if decision.decision == "APPROVE":
            ticket = f" Your refund ticket is {decision.refund_id}." if decision.refund_id else ""
            return f"Your refund request was approved.{ticket}"
        if decision.decision == "REVIEW":
            ticket = f" Your refund ticket is {decision.refund_id}." if decision.refund_id else ""
            return f"Your refund request requires further review.{ticket}"
        if decision.decision == "REJECT":
            return decision.message_context
        return "Your refund request could not be processed right now. Please try again shortly."


refund_chat_orchestrator = RefundChatOrchestrator()
