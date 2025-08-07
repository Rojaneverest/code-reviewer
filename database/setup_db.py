import psycopg2
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import DB_CONFIG

def setup_database():
    """Sets up the PostgreSQL database, creating the rules table with the vector column and inserting initial data."""
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Drop the rules table if it exists
        print('Dropping table "rules" if it exists...')
        cursor.execute("DROP TABLE IF EXISTS rules;")

        # Create the rules table with the vector column
        print('Creating table "rules"...')
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id SERIAL PRIMARY KEY,
            code_pattern TEXT NOT NULL,
            language TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            practice_type TEXT NOT NULL DEFAULT 'bad',
            last_updated_utc TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vector FLOAT[],  -- Add the vector column here
            UNIQUE (language, title)
        );
        """)

        # Insert initial data from SQL file
        print('Inserting initial data from "database/insert_rules.sql"...')
        sql_file_path = os.path.join(os.path.dirname(__file__), 'insert_rules.sql')
        with open(sql_file_path, 'r') as f:
            cursor.execute(f.read())

        conn.commit()
        print('Database setup completed successfully.')

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('Database connection closed.')

if __name__ == '__main__':
    setup_database()