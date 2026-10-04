from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.domain.enums.refund import RefundStatus

class CreateRefundRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transaction_id: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=3, max_length=2000)
    amount: Decimal | None = Field(default=None, gt=0)
    @field_validator("reason")
    @classmethod
    def clean_reason(cls, v: str) -> str:
        v = v.strip()
        if not v: raise ValueError("Refund reason is required.")
        return v

class RefundResponse(BaseModel):
    id: str
    user_id: str
    transaction_id: str
    order_id: str
    amount: Decimal
    currency: str
    reason: str
    status: RefundStatus
    decision: str | None
    created_at: datetime
    updated_at: datetime

class PaginatedRefunds(BaseModel):
    items: list[RefundResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class RefundSummary(BaseModel):
    created: int
    approved: int
    rejected: int
    escalated: int

class AdminRefundQuery(BaseModel):
    page: int = Field(default=1, ge=1, le=100000)
    page_size: int = Field(default=10, ge=1, le=100)
    status: RefundStatus | None = None
    refund_id: str | None = Field(default=None, max_length=64)
    created_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")

class ReviewRefundRequest(BaseModel):
    decision: str = Field(pattern=r"^(APPROVE|REJECT)$")
    note: str | None = Field(default=None, max_length=2000)
