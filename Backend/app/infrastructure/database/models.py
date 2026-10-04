from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, Numeric, String, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.enums.refund import RefundStatus
from app.domain.enums.transaction import TransactionStatus
from app.domain.enums.user import Role


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column("passwordHash", String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SAEnum(Role, name="Role", native_enum=True), default=Role.CUSTOMER, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")
    refunds: Mapped[list["Refund"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="actor")


class Transaction(Base):
    __tablename__ = "Transaction"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column("orderId", String(100), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column("userId", String(36), ForeignKey("User.id"), nullable=False, index=True)
    account_name: Mapped[str] = mapped_column("accountName", String(150), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus, name="TransactionStatus", native_enum=True),
        default=TransactionStatus.COMPLETED,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    final_sale: Mapped[bool] = mapped_column("finalSale", Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    refunded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="transactions")
    refunds: Mapped[list["Refund"]] = relationship(back_populates="transaction")


class Refund(Base):
    __tablename__ = "Refund"
    __table_args__ = (
        Index("Refund_userId_createdAt_idx", "userId", "createdAt"),
        Index("Refund_status_createdAt_idx", "status", "createdAt"),
        Index("Refund_orderId_idx", "orderId"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column("orderId", String(100), nullable=False)
    account_name: Mapped[str] = mapped_column("accountName", String(150), nullable=False)
    user_id: Mapped[str] = mapped_column("userId", String(36), ForeignKey("User.id"), nullable=False)
    transaction_id: Mapped[str] = mapped_column("transactionId", String(36), ForeignKey("Transaction.id"), nullable=False)
    request_id: Mapped[str | None] = mapped_column("requestId", String(64), unique=True, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[RefundStatus] = mapped_column(
        SAEnum(RefundStatus, name="RefundStatus", native_enum=True),
        default=RefundStatus.PENDING,
        nullable=False,
    )
    decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="refunds")
    transaction: Mapped[Transaction] = relationship(back_populates="refunds")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="refund")


class AuditLog(Base):
    __tablename__ = "AuditLog"
    __table_args__ = (
        Index("AuditLog_createdAt_idx", "createdAt"),
        Index("AuditLog_refundId_createdAt_idx", "refundId", "createdAt"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    refund_id: Mapped[str | None] = mapped_column("refundId", String(36), ForeignKey("Refund.id"), nullable=True)
    actor_type: Mapped[str] = mapped_column("actorType", String(50), nullable=False)
    actor_id: Mapped[str | None] = mapped_column("actorId", String(36), ForeignKey("User.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    note: Mapped[str] = mapped_column(String(4000), nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)

    refund: Mapped[Refund | None] = relationship(back_populates="audit_logs")
    actor: Mapped[User | None] = relationship(back_populates="audit_logs", foreign_keys=[actor_id])


class IdempotencyKey(Base):
    __tablename__ = "IdempotencyKey"
    __table_args__ = (Index("IdempotencyKey_userId_expiresAt_idx", "userId", "expiresAt"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column("userId", String(36), nullable=False)
    request_hash: Mapped[str] = mapped_column("requestHash", String(64), nullable=False)
    response_id: Mapped[str | None] = mapped_column("responseId", String(36), nullable=True)
    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
