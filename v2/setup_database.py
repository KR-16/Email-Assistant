import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from urllib.parse import urlparse  # Better URL parsing

# Load environment variables
load_dotenv()

def setup_database():
    # Get database connection details from environment variables
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    try:
        # Parse the database URL properly
        parsed = urlparse(db_url)
        
        # Extract components
        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432  # Default PostgreSQL port
        db_name = parsed.path[1:]  # Remove leading slash

        if not all([username, password, host, db_name]):
            raise ValueError("Invalid DATABASE_URL format")

        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            dbname='postgres'  # Connect to default DB to create our DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE {db_name}')
            print(f"Database '{db_name}' created successfully")
            
            # Optional: Create extensions
            cursor.execute(f"CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
        else:
            print(f"Database '{db_name}' already exists")

        cursor.close()
        conn.close()

        print("Database setup completed successfully")

    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database()