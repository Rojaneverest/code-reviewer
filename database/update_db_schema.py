import psycopg2
import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

def update_schema():
    """Adds a vector column to the rules table."""
    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("Altering table rules to add vector column...")
        # Add the vector column to store rule embeddings. Using FLOAT[] for compatibility.
        # The size of the vector will depend on the embedding model used.
        cur.execute("ALTER TABLE rules ADD COLUMN IF NOT EXISTS vector FLOAT[];")
        
        conn.commit()
        print("Schema updated successfully. 'vector' column added to 'rules' table.")

        cur.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    update_schema()
