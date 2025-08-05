import psycopg2
import sys
import os
from sentence_transformers import SentenceTransformer

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

def vectorize_rules():
    """Fetches rules, generates embeddings, and stores them in the database."""
    # Load a pre-trained sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Fetch all rules that haven't been vectorized yet
        print("Fetching rules from the database...")
        cur.execute("SELECT id, title, description, category FROM rules WHERE vector IS NULL;")
        rules = cur.fetchall()

        if not rules:
            print("All rules are already vectorized.")
            return

        print(f"Found {len(rules)} rules to vectorize...")

        for rule_id, title, description, category in rules:
            # Combine the text fields to create a rich context for the embedding
            combined_text = f"{title}. Category: {category}. Description: {description}"
            
            # Generate the embedding
            embedding = model.encode(combined_text).tolist()
            
            # Update the rule in the database with the new vector
            cur.execute("UPDATE rules SET vector = %s WHERE id = %s;", (embedding, rule_id))
            print(f"Vectorized and updated rule ID: {rule_id}")

        conn.commit()
        print("All rules have been vectorized and stored successfully.")

        cur.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    vectorize_rules()
