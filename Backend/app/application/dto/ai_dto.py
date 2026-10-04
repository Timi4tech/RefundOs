from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class RefundIntent(BaseModel):
    """Structured data extracted from a customer message by Gemini."""

    intent: Literal["refund_request", "refund_status", "general_support", "unknown"]
    transaction_id: str | None = Field(default=None, max_length=64)
    # Gemini's response_schema rejects Decimal and "gt" (exclusiveMinimum), so this is a
    # plain float here. RefundWorkerRequest converts it to Decimal and enforces amount > 0.
    amount: float | None = None
    reason: str | None = Field(default=None, max_length=2000)
    missing_fields: list[Literal["transaction_id", "reason", "amount"]] = Field(default_factory=list, max_length=3)

    @field_validator("amount")
    @classmethod
    def _non_positive_amount_is_missing(cls, v: float | None) -> float | None:
        # Runs after parsing, so it does not appear in the schema sent to Gemini.
        return v if v is not None and v > 0 else None


class RefundWorkerRequest(BaseModel):
    """Validated internal message sent from the chat/API layer to the refund worker."""

    request_id: str = Field(min_length=1, max_length=64)
    user_id: str = Field(min_length=1, max_length=64)
    transaction_id: str = Field(min_length=1, max_length=64)
    amount: Decimal | None = Field(default=None, gt=0)
    reason: str = Field(min_length=3, max_length=2000)


class ConversationalResponse(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class RefundWorkerDecision(BaseModel):
    request_id: str
    decision: Literal["APPROVE", "REJECT", "REVIEW", "ERROR"]
    status: str
    message_context: str
    refund_id: str | None = None
    ticket_created: bool = False
    transaction_status: str | None = None
    requested_amount: Decimal | None = None
    approved_amount: Decimal | None = None
    policy_note: str | None = None