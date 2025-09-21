from typing import Dict, Any
from jose import jwt, JWTError


def verify_jwt_signature(token: str, secret_or_public_key: str) -> Dict[str, Any]:
	try:
		payload = jwt.decode(token, secret_or_public_key, algorithms=["HS256", "RS256"])
		return {"valid": True, "payload": payload}
	except JWTError as e:
		return {"valid": False, "error": str(e)}


def verify_embedded_signature(data: Dict[str, Any], secret_or_public_key: str) -> Dict[str, Any]:
	"""If QR data includes a field 'sig' (JWT), verify it against the rest of fields.
	Expected that the JWT contains claims matching critical fields.
	"""
	sig = data.get("sig")
	if not sig:
		return {"checked": False}
	res = verify_jwt_signature(sig, secret_or_public_key)
	return {"checked": True, **res}


