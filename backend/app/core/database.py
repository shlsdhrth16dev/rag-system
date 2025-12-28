from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from app.core.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine
# pool_pre_ping=True helps handle DB connection drops
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # Gemini embedding dim
    doc_metadata = Column(Text)  # JSON string
    source = Column(String(500))
    created_at = Column(DateTime)
    
    # Create index for fast similarity search
    __table_args__ = (
        Index('embedding_idx', embedding, postgresql_using='ivfflat'),
    )
