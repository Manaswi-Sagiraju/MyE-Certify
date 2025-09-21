from __future__ import annotations

from io import BytesIO
from typing import List, Tuple
import math
import cv2
import numpy as np
from PIL import Image


def _first_image_from_bytes(data: bytes, filename: str | None) -> Image.Image | None:
	try:
		if (filename or "").lower().endswith(".pdf"):
			# PDF disabled in local mode
			return None
		else:
			return Image.open(BytesIO(data)).convert("RGB")
	except Exception:
		return None


def _phash(img: Image.Image, hash_size: int = 16) -> np.ndarray:
	# Perceptual hash via DCT
	img = img.convert("L").resize((hash_size * 4, hash_size * 4), Image.BICUBIC)
	arr = np.asarray(img, dtype=np.float32)
	dct = cv2.dct(arr)
	dct_low = dct[:hash_size, :hash_size]
	median = np.median(dct_low)
	return (dct_low > median).astype(np.uint8)


def _hamming(a: np.ndarray, b: np.ndarray) -> int:
	return int(np.count_nonzero(a.flatten() != b.flatten()))


def _template_match_scores(img: Image.Image, templates: List[Image.Image]) -> List[float]:
	scores: List[float] = []
	img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
	for t in templates:
		t_gray = cv2.cvtColor(np.array(t), cv2.COLOR_RGB2GRAY)
		th, tw = t_gray.shape[:2]
		if img_gray.shape[0] < th or img_gray.shape[1] < tw:
			scores.append(0.0)
			continue
		res = cv2.matchTemplate(img_gray, t_gray, cv2.TM_CCOEFF_NORMED)
		_, max_val, _, _ = cv2.minMaxLoc(res)
		scores.append(float(max_val))
	return scores


async def analyze_anomalies(file_bytes: bytes, filename: str | None) -> List[str]:
	"""Return anomaly warnings using pHash comparison and simple template matching.

	In this scaffold, we don't have canonical templates or a registry of known pHashes.
	So we compute a self-consistency check: if image is excessively compressed/noisy or
	if template matching against provided samples is low (no samples by default),
	we add soft warnings.
	"""
	warnings: List[str] = []
	img = _first_image_from_bytes(file_bytes, filename)
	if img is None:
		return warnings

	# Compression/noise heuristic: variance of Laplacian for blur detection
	gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
	blur_metric = cv2.Laplacian(gray, cv2.CV_64F).var()
	if blur_metric < 20:
		warnings.append("Low detail/blur detected; possible scan or tampering")

	# Blockiness (compression artifacts)
	blockiness = float(np.mean(np.abs(np.diff(gray.astype(np.int16), axis=1))))
	if blockiness < 1.2:
		warnings.append("Strong compression artifacts; image quality may affect OCR/validation")

	# pHash exists (no comparison yet). Could be used to compare with authoritative hash later.
	_ = _phash(img)

	# Template matching placeholder (no templates bundled)
	# If templates provided in future, use _template_match_scores to validate seals/logos.

	# Simple layout validation: text density by quadrants
	h, w = gray.shape
	quadrants = [
		gray[0:h//2, 0:w//2],
		gray[0:h//2, w//2:w],
		gray[h//2:h, 0:w//2],
		gray[h//2:h, w//2:w],
	]
	binarized = [cv2.threshold(q, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1] for q in quadrants]
	ink_ratio = [float(1.0 - (np.mean(b) / 255.0)) for b in binarized]
	if max(ink_ratio) > 0.65 and min(ink_ratio) < 0.05:
		warnings.append("Unusual text layout distribution; verify template positioning")

	# ELA (Error Level Analysis) style heuristic: recompress as JPEG and diff
	try:
		buf = BytesIO()
		img.save(buf, format="JPEG", quality=90)
		recompressed = Image.open(BytesIO(buf.getvalue())).convert("RGB")
		diff = cv2.absdiff(np.array(img), np.array(recompressed))
		ela_score = float(np.mean(diff))
		if ela_score > 10.0:
			warnings.append("ELA indicates potential local edits or heavy recompression")
	except Exception:
		pass

	return warnings


