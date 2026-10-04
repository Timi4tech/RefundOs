from dataclasses import dataclass, field
from datetime import datatime, timezone
from typing import Any
from uuid import uuid4

from app.domain.enums.audit import (AuditAction, AuditActionType)

@dataclass 
class AuditLog:
    
    id:str(uuid4)
    refund_ticket_id:str|None = None
    actor_type: AuditActorType = AuditActorType.System
    actor_id: str(uuid4) | None = None
    action: AuditAction = AuditAction.SECURITY
    note: str = ""
    metadata : dict[str,Any] | None = None
    created_at: datetime = field(default_factory = lambda:datetime.now(timezone.utc))
