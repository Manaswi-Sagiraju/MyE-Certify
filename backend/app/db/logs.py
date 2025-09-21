from typing import Optional
from sqlmodel import SQLModel, Field


class VerificationLog(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	timestamp_ms: int
	source_ip: str | None = None
	file_name: str | None = None
	success: bool
	score: float
	certificate_id: str | None = None
	roll_number: str | None = None
	institution_id: str | None = None
	message: str | None = None


