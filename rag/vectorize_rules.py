import psycopg2
import sys
import os
import numpy as np
from typing import List, Dict, Any
import logging

# Set project root and add it to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from config import DB_CONFIG
from rag.embedding_service import get_embedding_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def combine_rule_text(rule: Dict[str, Any]) -> str:
    """Combine rule components into a single text for embedding."""
    components = [
        f"Title: {rule['title']}",
        f"Code Pattern: {rule['code_pattern']}",
        f"Example: {rule['example_snippet']}" if rule['example_snippet'] else "",
        f"Description: {rule['description']}",
        f"Category: {rule['category']}"
    ]
    return " ".join(filter(bool, components))

def vectorize_rules():
    """Fetches rules, generates embeddings using the configured embedding service, and stores them in the database."""
    embedding_service = get_embedding_service()
    conn = None
    
    try:
        logger.info("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Fetch all rules that haven't been vectorized yet
        logger.info("Fetching rules from the database...")
        cur.execute("""
            SELECT id, title, description, category, code_pattern, example_snippet 
            FROM rules 
            WHERE vector IS NULL;
        """)
        rules = cur.fetchall()

        if not rules:
            logger.info("All rules are already vectorized.")
            return

        logger.info(f"Found {len(rules)} rules to vectorize...")

        # Process each rule
        for rule in rules:
            rule_dict = {
                'id': rule[0],
                'title': rule[1],
                'description': rule[2],
                'category': rule[3],
                'code_pattern': rule[4],
                'example_snippet': rule[5]
            }
            
            # Combine text for embedding
            combined_text = combine_rule_text(rule_dict)
            
            try:
                # Generate the embedding
                embedding = embedding_service.get_embedding(combined_text)
                
                # Update the database
                cur.execute(
                    "UPDATE rules SET vector = %s, last_updated_utc = CURRENT_TIMESTAMP WHERE id = %s",
                    (embedding.tolist(), rule_dict['id'])
                )
                conn.commit()
                logger.info(f"Updated vector for rule {rule_dict['id']}: {rule_dict['title']}")
                
            except Exception as e:
                logger.error(f"Error processing rule {rule_dict['id']}: {e}")
                conn.rollback()

    except Exception as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def vectorize_sql_code(sql_code: str) -> np.ndarray:
    """Generate embedding for SQL code using the configured embedding service."""
    embedding_service = get_embedding_service()
    return embedding_service.get_embedding(sql_code)

if __name__ == "__main__":
    vectorize_rules()
