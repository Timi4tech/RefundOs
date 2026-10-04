from dataclasses import dataclass
from dataclasses import dataclass, field
from datetime import datatime, timezone
from typing import Any
from uuid import uuid4


from app.domain.enums.audit import AuditActorType, AuditAction

@dataclass
class AuditLog_query_dto:
    refund_ticket_id:str|None = None
    actor_type: AuditActorType = AuditActorType.System
    actor_id: str | None = None
    action: AuditAction = AuditAction
    note: str = ""
    metadata : dict[str,Any] | None = None
    created_at: datetime = field(default_factory = lambda:datetime.now(timezone.utc))

@dataclass
class AuditLog_response_dto:
    id:str
    refund_ticket_id:str|None = None
    actor_type: AuditActorType = AuditActorType.System
    actor_id: str | None = None
    action: AuditAction = AuditAction
    note: str = ""
    metadata : dict[str,Any] | None = None
    created_at: datetime = field(default_factory = lambda:datetime.now(timezone.utc))