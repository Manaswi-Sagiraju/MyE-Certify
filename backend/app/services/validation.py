from typing import Dict, Any, List
from sqlmodel import Session, select
from ..db.models import CertificateRecord
from ..db.session import engine


async def validate_certificate_data(fields: Dict[str, Any], institution_id: str | None) -> Dict[str, Any]:
	"""Validate extracted fields against DB records.

	Placeholder for DB/ledger checks, signature validation, format checks,
	and anomaly detection.
	"""
	matched_fields: Dict[str, Any] = {}
	mismatched_fields: Dict[str, Any] = {}
	warnings: List[str] = []

	with Session(engine) as session:
		stmt = select(CertificateRecord)
		if institution_id:
			stmt = stmt.where(CertificateRecord.institution_id == institution_id)

		records = session.exec(stmt).all()

		def score_match(r: CertificateRecord) -> int:
			s = 0
			if fields.get("certificate_id") and r.certificate_id == fields.get("certificate_id"):
				s += 3
			if fields.get("roll_number") and r.roll_number == fields.get("roll_number"):
				s += 2
			if fields.get("candidate_name") and r.candidate_name.lower() == fields.get("candidate_name", "").lower():
				s += 1
			return s

		best = max(records, key=score_match) if records else None

	if not best:
		return {
			"is_valid": False,
			"confidence": 0.2,
			"message": "No matching record found",
			"matched_fields": {},
			"mismatched_fields": {k: v for k, v in fields.items()},
			"warnings": ["Connect to authoritative registry to improve accuracy."],
		}

	for key in ["certificate_id", "roll_number", "candidate_name", "course"]:
		if key in fields and fields[key] is not None:
			expected = getattr(best, key, None)
			if expected is not None and str(fields[key]).lower() == str(expected).lower():
				matched_fields[key] = fields[key]
			else:
				mismatched_fields[key] = {"provided": fields[key], "expected": expected}

	confidence = 0.45 + 0.15 * len(matched_fields) - 0.1 * len(mismatched_fields)
	confidence = max(0.0, min(0.99, confidence))

	is_valid = bool(matched_fields) and not ("certificate_id" in mismatched_fields)
	message = "Certificate appears valid" if is_valid else "Potential forgery or data mismatch"

	return {
		"is_valid": is_valid,
		"confidence": round(confidence, 2),
		"message": message,
		"matched_fields": matched_fields,
		"mismatched_fields": mismatched_fields,
		"warnings": warnings,
	}


