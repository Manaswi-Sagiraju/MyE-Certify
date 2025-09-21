from io import BytesIO
from typing import Dict
from fastapi import UploadFile
from PIL import Image, ImageFilter
import pytesseract
import cv2
import numpy as np
import re


def _preprocess_image_for_ocr(img: Image.Image) -> Image.Image:
	# convert to grayscale, denoise, threshold
	arr = np.array(img.convert("RGB"))
	gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
	gray = cv2.bilateralFilter(gray, 9, 75, 75)
	thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
	return Image.fromarray(thr)


def _extract_text_from_image(img: Image.Image) -> str:
	proc = _preprocess_image_for_ocr(img)
	config = "--oem 3 --psm 6"
	return pytesseract.image_to_string(proc, config=config)


def _pdf_to_images(_: bytes) -> list[Image.Image]:
	# Disabled without PyMuPDF; return empty list
	return []


async def extract_text_fields(file: UploadFile) -> Dict[str, str]:
	"""OCR for images/PDF with naive parsing of fields.

	Falls back to filename heuristics if OCR fails.
	"""
	content = await file.read()
	await file.seek(0)

	text = ""
	try:
		if (file.filename or "").lower().endswith(".pdf"):
			# PDF support disabled; rely on filename heuristics
			text = ""
		else:
			img = Image.open(BytesIO(content))
			text = _extract_text_from_image(img)
	except Exception:
		text = ""

	fields: Dict[str, str] = {}

	def find_after(label: str) -> str | None:
		for line in text.splitlines():
			if label.lower() in line.lower():
				part = line.split(":", 1)
				if len(part) == 2:
					val = part[1].strip()
					return val[:128]
		return None

	fields_candidates = {
		"candidate_name": ["name", "candidate", "student name"],
		"roll_number": ["roll", "roll no", "roll number"],
		"certificate_id": ["certificate id", "certificate no", "cert id"],
		"course": ["course", "program", "degree"],
	}

	for key, labels in fields_candidates.items():
		for label in labels:
			val = find_after(label)
			if val:
				fields[key] = val
				break

	# Regex-based extraction if labels not found
	text_flat = " ".join(text.split())
	patterns = {
		"certificate_id": r"(CERT[-\s]?\d{4}[-\s]?\d{3,5})",
		"roll_number": r"(RJH\d{4,8}|ROLL\s?No\.?\s?[A-Za-z0-9-]+)",
	}
	for k, pat in patterns.items():
		if k not in fields:
			m = re.search(pat, text_flat, flags=re.IGNORECASE)
			if m:
				fields[k] = m.group(1)

	# Fallback to filename heuristics if still missing
	if not fields:
		name = (file.filename or "").rsplit("/", 1)[-1]
		base = name.rsplit(".", 1)[0]
		parts = [p for p in base.replace("-", " ").replace("_", " ").split(" ") if p]
		if parts:
			fields["candidate_name"] = parts[0].title()
		if len(parts) > 1:
			fields["roll_number"] = parts[1]
		if len(parts) > 2:
			fields["certificate_id"] = parts[2]
		if len(parts) > 3:
			fields["course"] = " ".join(parts[3:]).title()

	return fields


