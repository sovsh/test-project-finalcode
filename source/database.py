from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://docker:secret@database/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)