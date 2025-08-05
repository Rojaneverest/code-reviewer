import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

# Initialize the sentence transformer model globally to avoid reloading it on every call
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

def find_relevant_rules(code_chunk, language='SQL', top_k=5, similarity_threshold=0.35):
    """Finds the most relevant rules for a code chunk using vector similarity search."""
    conn = None
    relevant_rules = [] # Simplified to a single list

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Perform vector search for semantic relevance against the new table
        print(f"\nRunning vector similarity search...\n---\n{code_chunk[:200]}...\n---")
        code_embedding = model.encode(code_chunk, convert_to_tensor=False)
        
        # Query the new vector_rules table
        cur.execute(
            "SELECT id, title, description, severity, category, suggestion, vector FROM vector_rules WHERE language = %s AND vector IS NOT NULL;",
            (language,)
        )
        rules_data = cur.fetchall()
        
        if not rules_data:
            print("No vectorized rules found in 'vector_rules' table.")
            return relevant_rules

        rule_similarities = []
        for rule in rules_data:
            rule_id, title, description, severity, category, suggestion, vector = rule
            if vector:
                # Calculate cosine similarity
                similarity = np.dot(code_embedding, np.array(vector)) / (np.linalg.norm(code_embedding) * np.linalg.norm(np.array(vector)))
                if similarity > similarity_threshold:
                    rule_similarities.append((similarity, {
                        'id': rule_id, 
                        'title': title, 
                        'description': description,
                        'severity': severity, 
                        'category': category,
                        'suggestion': suggestion
                    }))

        # Sort by similarity and get the top_k results
        rule_similarities.sort(key=lambda x: x[0], reverse=True)
        relevant_rules = [rule for _, rule in rule_similarities[:top_k]]

        print(f"Found {len(relevant_rules)} semantically relevant rules with similarity > {similarity_threshold}.")
        for rule in relevant_rules:
            print(f"  -> Found relevant rule: '{rule['title']}'")

        return relevant_rules

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return relevant_rules
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return relevant_rules
    finally:
        if conn is not None:
            conn.close()
