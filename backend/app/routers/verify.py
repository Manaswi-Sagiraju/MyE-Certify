from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi import Depends
from typing import Optional

from ..services.ocr import extract_text_fields
from ..services.qr import decode_qr_from_file
from ..services.validation import validate_certificate_data
from ..models.schemas import VerificationResponse, VerificationDetails
from sqlmodel import Session
from ..db.session import get_session
from ..db.logs import VerificationLog
import time
from ..services.signature import verify_embedded_signature
from ..services.url_validate import validate_qr_url
from ..services.anomaly import analyze_anomalies


router = APIRouter()


@router.post("/upload", response_model=VerificationResponse)
async def upload_and_verify(
	file: UploadFile = File(...),
	institution_id: Optional[str] = None,
	session: Session = Depends(get_session),
	request: Request = None,
):
	if not file.filename:
		raise HTTPException(status_code=400, detail="No file provided")

	# Extract via OCR
	ocr_fields = await extract_text_fields(file)

	# Try QR
	qr_data = await decode_qr_from_file(file)

	# Prefer QR data if present, else OCR
	merged = {**ocr_fields}
	if qr_data:
		merged.update(qr_data)

	# Signature check if QR carries 'sig'
	sig_info = {"checked": False}
	if qr_data and isinstance(qr_data, dict) and qr_data.get("sig"):
		sig_info = verify_embedded_signature(qr_data, secret_or_public_key="dev-secret-change-me")

	# If QR contains a URL, validate it
	url_warning = None
	if qr_data and isinstance(qr_data, dict):
		qr_url = qr_data.get("url") or qr_data.get("verify_url")
		if qr_url:
			ok, info = await validate_qr_url(qr_url)
			if not ok:
				url_warning = f"QR URL validation failed: {info}"

	# Validate (DB)
	validation = await validate_certificate_data(merged, institution_id=institution_id)

	# Log verification
	try:
		log = VerificationLog(
			timestamp_ms=int(time.time() * 1000),
			source_ip=request.client.host if request and request.client else None,
			file_name=file.filename,
			success=validation["is_valid"],
			score=float(validation["confidence"]),
			certificate_id=merged.get("certificate_id"),
			roll_number=merged.get("roll_number"),
			institution_id=institution_id,
			message=validation.get("message"),
		)
		session.add(log)
		session.commit()
	except Exception:
		pass

	# Anomaly analysis (image-level)
	file_bytes = await file.read()
	await file.seek(0)
	anomaly_warnings = await analyze_anomalies(file_bytes, file.filename)

	return VerificationResponse(
		success=validation["is_valid"],
		score=validation["confidence"],
		message=validation["message"],
		details=VerificationDetails(
			matched_fields=validation.get("matched_fields", {}),
			mismatched_fields=validation.get("mismatched_fields", {}),
			warnings=[
				*validation.get("warnings", []),
				*([] if sig_info.get("valid", False) or not sig_info.get("checked") else ["Signature invalid or unverifiable"]),
				*([] if not url_warning else [url_warning]),
				*anomaly_warnings,
			],
		),
	)


