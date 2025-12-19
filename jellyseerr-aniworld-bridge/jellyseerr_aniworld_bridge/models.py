import datetime as dt
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
import enum

Base = declarative_base()


class JobStatus(enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DownloadJob(Base):
    __tablename__ = "download_jobs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, nullable=True)
    show_name = Column(String, nullable=False)
    aniworld_url = Column(String, nullable=True)
    season = Column(Integer, nullable=True)
    episode = Column(Integer, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    filepath = Column(String, nullable=True)


engine = None
SessionLocal = None

def initialize_db(database_url: str):
    global engine, SessionLocal
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db_session():
    if SessionLocal is None:
        raise Exception("Database not initialized. Call initialize_db() first.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
