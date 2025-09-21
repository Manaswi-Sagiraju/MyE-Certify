import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-env")
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode.update({"exp": expire})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		if not payload.get("sub"):
			raise HTTPException(status_code=401, detail="Invalid token")
		return payload
	except JWTError:
		raise HTTPException(status_code=401, detail="Invalid token")


def require_role(required_role: str):
	def _dep(user: dict = Depends(get_current_user)) -> dict:
		role = user.get("role")
		if role != required_role:
			raise HTTPException(status_code=403, detail="Insufficient role")
		return user
	return _dep


