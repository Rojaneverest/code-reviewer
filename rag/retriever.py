import psycopg2
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import DB_CONFIG

def retrieve_relevant_rules(code_chunk, language):
    """Retrieves relevant rules from the PostgreSQL database for a given code chunk and language."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # A simple query to fetch all rules for the given language
        # This can be improved with more sophisticated matching logic
        query = "SELECT * FROM rules WHERE language = %s;"
        cursor.execute(query, (language,))
        rules = cursor.fetchall()
        return rules

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()
