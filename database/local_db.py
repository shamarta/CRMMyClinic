from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings
from .models import Base

logger = logging.getLogger(__name__)


class LocalDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.local_db_path
        self.engine = None
        self.SessionLocal = None
        self._initialize()

    def _initialize(self):
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Local database initialized at: {self.db_path}")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    def get_db(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def close(self):
        if self.engine:
            self.engine.dispose()
            logger.info("Local database connection closed")


local_db = LocalDatabase()
