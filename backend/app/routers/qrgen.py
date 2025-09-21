from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO


router = APIRouter(prefix="/qr", tags=["qr"])


@router.get("/certificate/{institution_id}/{certificate_id}")
def qr_for_certificate(institution_id: str, certificate_id: str):
	url = f"http://localhost:8000/v/{certificate_id}"
	img = qrcode.make({
		"certificate_id": certificate_id,
		"institution_id": institution_id,
		"url": url,
	})
	buf = BytesIO()
	img.save(buf, format="PNG")
	buf.seek(0)
	return StreamingResponse(buf, media_type="image/png")





