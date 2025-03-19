import os
import time
from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables (useful for local development)
load_dotenv()

# Database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "price_calculator")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# PostgreSQL database URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Maximum number of retries for database connection
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

def create_db_engine():
    """Create database engine with retry logic"""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Create database engine
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_pre_ping=True  # Enable connection health checks
            )
            # Test the connection
            engine.connect()
            print("Successfully connected to the database")
            return engine
        except exc.OperationalError as e:
            if retries < MAX_RETRIES - 1:
                retries += 1
                print(f"Database connection attempt {retries} failed. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Failed to connect to the database after multiple attempts")
                raise e

# Create engine with retry logic
engine = create_db_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
