from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .entities import Base

DB_PATH = Path(__file__).parent.parent.parent / "data" / "rantevou.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{str(DB_PATH)}"

if not DB_PATH.exists():
    DB_PATH.open("wb").close()


engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
