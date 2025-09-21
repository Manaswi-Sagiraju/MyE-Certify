from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.verify import router as verify_router


app = FastAPI(title="Authenticity Validator for Academia", version="0.1.0")

# CORS - adjust origins in production
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/health")
def health_check():
	return {"status": "ok"}


app.include_router(verify_router, prefix="/verify", tags=["verification"])


