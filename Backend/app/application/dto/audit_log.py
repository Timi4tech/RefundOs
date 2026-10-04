from datetime import datetime
from pydantic import BaseModel, Field
class AuditLogResponse(BaseModel):
    id: str
    refund_id: str | None
    actor_type: str
    actor_id: str | None
    action: str
    note: str
    metadata: dict | None
    created_at: datetime
class PaginatedAuditLogs(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
