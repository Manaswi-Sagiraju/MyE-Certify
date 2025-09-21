from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import time

from ..db.session import get_session
from ..db.models import CertificateRecord
from ..db.audit import AuditLog
from ..security.auth import require_role


router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.post("/{institution_id}/records")
def upsert_record(
	institution_id: str,
	record: CertificateRecord,
	session: Session = Depends(get_session),
	user=Depends(require_role("admin")),
):
	# Enforce path institution_id
	if record.institution_id != institution_id:
		raise HTTPException(status_code=400, detail="institution_id mismatch")

	existing = session.exec(
		select(CertificateRecord).where(
			CertificateRecord.institution_id == institution_id,
			CertificateRecord.certificate_id == record.certificate_id,
		)
	).first()
	if existing:
		existing.candidate_name = record.candidate_name
		existing.roll_number = record.roll_number
		existing.course = record.course
		existing.year = record.year
		action = "update"
	else:
		session.add(record)
		action = "insert"
	
	session.add(
		AuditLog(
			timestamp_ms=int(time.time() * 1000),
			actor=user.get("sub"),
			action=action,
			entity="CertificateRecord",
			entity_id=f"{record.institution_id}:{record.certificate_id}",
		)
	)
	session.commit()
	return {"status": "ok", "action": action}


@router.get("/{institution_id}/records/{certificate_id}")
def get_record(
	institution_id: str,
	certificate_id: str,
	session: Session = Depends(get_session),
	user=Depends(require_role("admin")),
):
	rec = session.exec(
		select(CertificateRecord).where(
			CertificateRecord.institution_id == institution_id,
			CertificateRecord.certificate_id == certificate_id,
		)
	).first()
	if not rec:
		raise HTTPException(status_code=404, detail="not found")
	return rec


