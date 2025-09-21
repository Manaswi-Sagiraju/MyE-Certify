from typing import Optional
from sqlmodel import SQLModel, Field


class CertificateRecord(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	institution_id: str = Field(index=True)
	certificate_id: str = Field(index=True)
	candidate_name: str = Field(index=True)
	roll_number: str = Field(index=True, alias="roll_number")
	course: str
	year: int


