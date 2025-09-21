import os
from typing import Tuple, Dict
from urllib.parse import urlparse, parse_qs
import httpx


async def validate_qr_url(url: str) -> Tuple[bool, Dict]:
	"""Validate QR URL by checking domain and optional fetch.

	Returns (ok, details)
	"""
	try:
		o = urlparse(url)
		if o.scheme not in {"http", "https"}:
			return False, {"reason": "invalid_scheme"}
		# Allowlist via env var QR_ALLOWED_DOMAINS (comma-separated)
		allowed_env = os.getenv("QR_ALLOWED_DOMAINS", "verify.jh.gov.in,example.edu,university.example")
		allowed = {d.strip() for d in allowed_env.split(",") if d.strip()}
		if o.hostname and o.hostname not in allowed:
			return False, {"reason": "untrusted_domain", "host": o.hostname}
		# Optional: fetch URL head
		async with httpx.AsyncClient(timeout=5) as client:
			resp = await client.get(url)
			if resp.status_code >= 400:
				return False, {"reason": "http_error", "status": resp.status_code}
		return True, {"status": "ok"}
	except Exception as e:
		return False, {"reason": "exception", "error": str(e)}


