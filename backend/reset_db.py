from app.core.database import Base, engine, Document

def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")
    
    # Init DB will handle creation
    from app.core.init_db import init_db
    init_db()
    print("Database re-initialized with new schema.")

if __name__ == "__main__":
    reset_db()
