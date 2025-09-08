from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging
import os

# Replace with your actual MySQL credentials
DATABASE_URL =f"sqlite:///test.db"

try:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except SQLAlchemyError as e:
    logging.error(f"Error connecting to the database: {e}")
    raise

def connect_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()