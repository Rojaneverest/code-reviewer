import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

model_path = r'C:\Users\RojanRajThapa\Desktop\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2'

# Initialize the sentence transformer model using the local path
print("Loading sentence transformer model from local cache...")
try:
    model = SentenceTransformer(model_path)
    print("Model loaded successfully.")
except Exception as e:
    print(f"An error occurred while loading the model: {e}")
    model = None  # Safeguard for failed loading

# Use an assertion to ensure the model is correctly loaded before using it
assert model is not None, "Model failed to load, ensure the correct path and files exist."

import re

def find_relevant_rules(code_chunk, language='SQL', top_k=3, similarity_threshold=0.55):
    """Finds the most relevant rules for a code chunk using vector similarity search."""
    conn = None
    relevant_rules = {'good_practices': [], 'bad_practices': []}

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Hybrid Approach: First, try to find direct violations with regex
        print(f"\nRunning regex search for bad practices...\n---\n{code_chunk[:200]}...\n---")
        cur.execute(
            "SELECT id, title, description, code_pattern, severity, practice_type, category FROM rules WHERE language = %s AND practice_type = 'bad' AND code_pattern IS NOT NULL;",
            (language,)
        )
        bad_practice_rules = cur.fetchall()

        matched_bad_rules = []
        for rule_id, title, description, code_pattern, severity, _, category in bad_practice_rules:
            if re.search(code_pattern, code_chunk, re.IGNORECASE):
                matched_bad_rules.append({
                    'id': rule_id, 'title': title, 'description': description, 
                    'severity': severity, 'practice_type': 'bad', 'category': category
                })

        # If any regex matches were found, we can return them without falling back to vector search.
        if matched_bad_rules:
            print(f"Found {len(matched_bad_rules)} direct violation(s) via regex.")
            relevant_rules['bad_practices'] = matched_bad_rules
            return relevant_rules, "Regex Match"

        # 2. If no regex match, fall back to vector search for semantic relevance
        print("No direct violations found. Falling back to vector similarity search...")
        code_embedding = model.encode(code_chunk, convert_to_tensor=False)
        cur.execute(
            "SELECT id, title, description, severity, practice_type, category, vector FROM rules WHERE language = %s AND vector IS NOT NULL;",
            (language,)
        )
        rules_data = cur.fetchall()
        
        if not rules_data:
            print("No vectorized rules found.")
            return relevant_rules, "Vector Search"

        rule_similarities = []
        for rule in rules_data:
            rule_id, title, description, severity, practice_type, category, vector = rule
            if vector:
                similarity = np.dot(code_embedding, np.array(vector)) / (np.linalg.norm(code_embedding) * np.linalg.norm(np.array(vector)))
                if similarity > similarity_threshold:
                    rule_similarities.append((similarity, {
                        'id': rule_id, 'title': title, 'description': description,
                        'severity': severity, 'practice_type': practice_type, 'category': category
                    }))

        rule_similarities.sort(key=lambda x: x[0], reverse=True)
        top_rules = [rule for _, rule in rule_similarities[:top_k]]

        print(f"Found {len(top_rules)} semantically relevant rules with similarity > {similarity_threshold}.")

        for rule in top_rules:
            if rule['practice_type'] == 'bad':
                relevant_rules['bad_practices'].append(rule)
            else:
                relevant_rules['good_practices'].append(rule)

        return relevant_rules, "Vector Search"

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return relevant_rules, "Error"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return relevant_rules, "Error"
    finally:
        if conn is not None:
            conn.close()
