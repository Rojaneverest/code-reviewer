import psycopg2
import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

def create_vector_rules_table():
    """Creates the vector_rules table for storing rules without regex patterns."""
    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("Dropping existing vector_rules table if it exists...")
        cur.execute("DROP TABLE IF EXISTS vector_rules;")

        print("Creating new vector_rules table...")
        cur.execute("""
            CREATE TABLE vector_rules (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(50) NOT NULL, -- 'good_practices' or 'bad_practices'
                severity VARCHAR(50),
                language VARCHAR(50) NOT NULL,
                suggestion TEXT,
                vector FLOAT[] -- To store sentence embeddings
            );
        """)
        
        conn.commit()
        print("Table 'vector_rules' created successfully.")

        cur.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_vector_rules_table()
