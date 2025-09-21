from typing import Dict
from fastapi import UploadFile
import cv2
import json
import numpy as np


def _decode_qr_from_image_bytes(data: bytes) -> Dict:
	img_array = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
	if img_array is None:
		return {}
	detector = cv2.QRCodeDetector()
	val, points, straight_qrcode = detector.detectAndDecode(img_array)
	if not val:
		return {}
	try:
		return json.loads(val)
	except Exception:
		return {"raw": val}


async def decode_qr_from_file(file: UploadFile) -> Dict:
	"""Decode QR/Barcode from image or first page of PDF if image-like.
	Returns dict with parsed data or empty if none.
	"""
	bytes_data = await file.read()
	await file.seek(0)
	# Try direct image
	try:
		res = _decode_qr_from_image_bytes(bytes_data)
		if res:
			return res
	except Exception:
		pass
	return {}


