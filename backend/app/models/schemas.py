from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class VerificationDetails(BaseModel):
	matched_fields: Dict[str, Any] = Field(default_factory=dict)
	mismatched_fields: Dict[str, Any] = Field(default_factory=dict)
	warnings: List[str] = Field(default_factory=list)


class VerificationResponse(BaseModel):
	success: bool
	score: float = Field(ge=0, le=1)
	message: str
	details: VerificationDetails


