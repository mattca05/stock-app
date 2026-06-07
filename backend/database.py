from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from backend.models import Base
from dotenv import load_dotenv
import os
import sys

if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle — .env is next to the .exe
    _base = os.path.dirname(sys.executable)
    load_dotenv(os.path.join(_base, ".env"))
else:
    load_dotenv()


class Database:
    _instance = None  # Singleton

    def __init__(self, db_path: str | None = None):
        path = db_path or os.getenv("DB_PATH", "")

        if not path:
            raise ValueError("DB_PATH is not set. Add it to your .env file.")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Database file not found: {path}")

        self.engine = create_engine(f"sqlite:///{path}")
        self._SessionLocal = sessionmaker(bind=self.engine)

    @classmethod
    def get_instance(cls) -> "Database":
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        s: Session = self._SessionLocal()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    def create_tables(self):
        Base.metadata.create_all(self.engine)
