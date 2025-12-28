from sqlalchemy import text
from app.core.database import engine, Base

def init_db():
    """Initialize database with pgvector extension"""
    with engine.connect() as conn:
        # Enable pgvector
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")
