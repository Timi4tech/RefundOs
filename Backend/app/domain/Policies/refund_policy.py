from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import re

from app.core.config import settings
from app.domain.enums.refund import RefundStatus
from app.domain.enums.transaction import TransactionStatus


@dataclass(frozen=True)
class RefundPolicyResult:
    status: RefundStatus
    decision: str
    note: str


class RefundPolicy:
    """Deterministic refund policy. Gemini never makes these decisions."""

    MAX_AUTO_APPROVAL = Decimal("500")

    _AUTO_APPROVABLE_REASONS = (
        "damaged",
        "damage",
        "incorrect item",
        "wrong item",
        "wrong product",
        "not received",
        "did not receive",
        "never arrived",
        "duplicate charge",
        "charged twice",
    )

    _SUSPICIOUS_PATTERNS = (
        r"chargeback",
        r"cash back",
        r"keep.*and.*refund",
        r"refund.*and.*keep",
        r"different.*transaction",
        r"another.*transaction",
        r"someone else.*transaction",
        r"use.*someone else",
        r"fake.*receipt",
        r"fraudulent.*refund",
        r"bypass.*policy",
    )

    _CONFLICTING_PATTERNS = (
        r"\b(received|delivered)\b.*\b(did not receive|never arrived|not received)\b",
        r"\b(did not receive|never arrived|not received)\b.*\b(received|delivered)\b",
        r"\b(used|opened)\b.*\b(never used|unused|unopened)\b",
        r"\b(never used|unused|unopened)\b.*\b(used|opened)\b",
        r"\b(correct|right) item\b.*\b(wrong|incorrect) item\b",
        r"\b(wrong|incorrect) item\b.*\b(correct|right) item\b",
    )

    @classmethod
    def evaluate(
        cls,
        amount: Decimal,
        transaction_status: TransactionStatus,
        reason: str,
        *,
        transaction_created_at: datetime,
        final_sale: bool,
        now: datetime | None = None,
    ) -> RefundPolicyResult:
        if amount <= 0:
            raise ValueError("Refund amount must be greater than zero.")

        if not reason.strip():
            raise ValueError("Refund reason is required.")

        if transaction_status != TransactionStatus.COMPLETED:
            return RefundPolicyResult(
                RefundStatus.REQUIRES_REVIEW,
                "REVIEW",
                "Only completed transactions can be automatically processed.",
            )

        if final_sale:
            return RefundPolicyResult(
                RefundStatus.REJECTED,
                "REJECT",
                "This order is marked as final sale and is not eligible for a refund.",
            )

        current_time = now or datetime.now(timezone.utc)
        created_at = transaction_created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age_days = (current_time - created_at).total_seconds() / 86400
        if age_days > settings.REFUND_WINDOW_DAYS:
            return RefundPolicyResult(
                RefundStatus.REJECTED,
                "REJECT",
                f"The order is older than the {settings.REFUND_WINDOW_DAYS}-day refund period and cannot be refunded.",
            )

        if amount > cls.MAX_AUTO_APPROVAL:
            return RefundPolicyResult(
                RefundStatus.REQUIRES_REVIEW,
                "REVIEW",
                "Refunds above $500 require human review.",
            )

        normalized_reason = " ".join(reason.lower().split())

        if cls._matches(normalized_reason, cls._SUSPICIOUS_PATTERNS):
            return RefundPolicyResult(
                RefundStatus.REQUIRES_REVIEW,
                "REVIEW",
                "The request contains information that requires human review for security and consistency.",
            )

        if cls._matches(normalized_reason, cls._CONFLICTING_PATTERNS):
            return RefundPolicyResult(
                RefundStatus.REQUIRES_REVIEW,
                "REVIEW",
                "The refund details contain conflicting information and require human review.",
            )

        if not any(term in normalized_reason for term in cls._AUTO_APPROVABLE_REASONS):
            return RefundPolicyResult(
                RefundStatus.REQUIRES_REVIEW,
                "REVIEW",
                "The refund reason does not meet an automatic approval condition and requires human review.",
            )

        return RefundPolicyResult(
            RefundStatus.APPROVED,
            "APPROVE",
            "The completed transaction is within the refund period, is not final sale, is within the automatic approval limit, and the stated reason qualifies for automatic approval.",
        )

    @staticmethod
    def _matches(value: str, patterns: tuple[str, ...]) -> bool:
        return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)
