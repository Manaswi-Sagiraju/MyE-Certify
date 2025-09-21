from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
import csv
import io
import time

from ..security.auth import create_access_token, get_password_hash, verify_password, require_role
from ..db.session import get_session
from ..db.models import CertificateRecord
from ..db.logs import VerificationLog


router = APIRouter(prefix="/admin", tags=["admin"])


# Demo admin user (replace with proper user store)
DEMO_ADMIN = {"username": "admin", "password_hash": get_password_hash("admin123"), "role": "admin"}


@router.post("/login")
def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
	if form_data.username != DEMO_ADMIN["username"] or not verify_password(form_data.password, DEMO_ADMIN["password_hash"]):
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	token = create_access_token({"sub": form_data.username, "role": DEMO_ADMIN["role"]})
	return {"access_token": token, "token_type": "bearer"}


@router.post("/bulk-upload")
def bulk_upload(
	file: UploadFile = File(...),
	session: Session = Depends(get_session),
	user=Depends(require_role("admin")),
):
	content = file.file.read().decode("utf-8", errors="ignore")
	reader = csv.DictReader(io.StringIO(content))
	count = 0
	for row in reader:
		record = CertificateRecord(
			institution_id=row.get("institution_id", "").strip(),
			certificate_id=row.get("certificate_id", "").strip(),
			candidate_name=row.get("candidate_name", "").strip(),
			roll_number=row.get("roll_number", "").strip(),
			course=row.get("course", "").strip(),
			year=int(row.get("year", 0) or 0),
		)
		session.add(record)
		count += 1
	
	session.commit()
	return {"inserted": count}


@router.get("/stats")
def stats(session: Session = Depends(get_session), user=Depends(require_role("admin"))):
	total_certs = session.exec(select(CertificateRecord)).all()
	logs = session.exec(select(VerificationLog)).all()
	success = len([l for l in logs if l.success])
	failure = len(logs) - success
	return {
		"certificates": len(total_certs),
		"verifications": {"total": len(logs), "success": success, "failure": failure},
	}


