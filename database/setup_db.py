import psycopg2
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import DB_CONFIG

def setup_database():
    """Sets up the PostgreSQL database, creating the vector_rules table and inserting initial data."""
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create the vector_rules table
        print('Dropping table "vector_rules" if it exists...')
        cursor.execute("DROP TABLE IF EXISTS vector_rules;")

        print('Creating table "vector_rules"...')
        cursor.execute("""
        CREATE TABLE vector_rules (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            severity VARCHAR(50),
            language VARCHAR(50) NOT NULL,
            suggestion TEXT,
            vector FLOAT[]
        );
        """)

        # Insert initial data from SQL file
        print('Inserting initial data from "database/insert_vector_rules.sql"...')
        sql_file_path = os.path.join(os.path.dirname(__file__), 'insert_vector_rules.sql')
        with open(sql_file_path, 'r') as f:
            cursor.execute(f.read())

        conn.commit()
        print('Database setup for vector_rules completed successfully.')

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('Database connection closed.')

if __name__ == '__main__':
    setup_database()
