import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import time
from dotenv import load_dotenv
from app.database import engine
from app.models import Base
from sqlalchemy import text

def wait_for_db(params: dict, max_retries: int = 30, retry_delay: int = 2):
    """Wait for the database to be ready"""
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=params['host'],
                port=params['port'],
                user=params['user'],
                password=params['password'],
                database='postgres'  # Connect to default database first
            )
            conn.close()
            print("Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            retries += 1
            if retries < max_retries:
                print(f"Database not ready. Retrying in {retry_delay} seconds... (Attempt {retries}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print("Failed to connect to the database after maximum retries")
                raise e

def create_database(params: dict):
    """Create the database if it doesn't exist"""
    try:
        # Connect to default database
        conn = psycopg2.connect(
            host=params['host'],
            port=params['port'],
            user=params['user'],
            password=params['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{params['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {params['database']}")
            print(f"Database '{params['database']}' created successfully")
        else:
            print(f"Database '{params['database']}' already exists")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def init_database():
    """Initialize the database with retries"""
    # Load environment variables
    load_dotenv()
    
    # Database connection parameters
    params = {
        'host': os.getenv("DB_HOST", "localhost"),
        'port': os.getenv("DB_PORT", "5432"),
        'database': os.getenv("DB_NAME", "price_calculator"),
        'user': os.getenv("DB_USER", "postgres"),
        'password': os.getenv("DB_PASSWORD", "postgres")
    }

    try:
        # Wait for database to be ready
        wait_for_db(params)
        
        # Create database
        create_database(params)
        
        # Create tables
        create_tables()
        
        # Test database connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection test successful!")
            
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_database()
