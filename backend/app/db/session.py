import os
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv


load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///./certificates.db")
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, echo=False, connect_args=connect_args)


def init_db() -> None:
	from . import models  # ensure models are imported
	from . import logs  # ensure logs table exists
	from . import audit  # ensure audit table exists
	SQLModel.metadata.create_all(engine)


def get_session() -> Session:
	with Session(engine) as session:
		yield session


