from typing import Optional
from sqlmodel import SQLModel, Field


class AuditLog(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	timestamp_ms: int
	actor: str
	action: str
	entity: str
	entity_id: str | None = None
	changes: str | None = None


