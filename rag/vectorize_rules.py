import psycopg2
import sys
import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Any
import logging

# Set project root and add it to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeEmbedder:
    def __init__(self):
        """Initialize the CodeT5 model for code-aware embeddings."""
        self.model_name = "Salesforce/codet5p-220m"
        self.local_model_path = r"C:\Users\RojanRajThapa\Desktop\huggingface\codet5p-220m"
        
        # Download and save model if not exists
        if not os.path.exists(self.local_model_path):
            logger.info(f"Downloading {self.model_name} model and tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModel.from_pretrained(self.model_name)
            
            logger.info(f"Saving model and tokenizer to {self.local_model_path}")
            tokenizer.save_pretrained(self.local_model_path)
            model.save_pretrained(self.local_model_path)
        
        # Load from local path
        logger.info(f"Loading model and tokenizer from {self.local_model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.local_model_path)
        self.model = AutoModel.from_pretrained(self.local_model_path)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"Model loaded successfully and running on {self.device}")

    def get_embedding(self, text: str, max_length: int = 512) -> np.ndarray:
        """Generate embedding for a given text using CodeT5."""
        with torch.no_grad():
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt"
            ).to(self.device)
            
            # Add empty decoder_input_ids
            decoder_input_ids = torch.zeros(
                (inputs.input_ids.shape[0], 1), 
                dtype=torch.long, 
                device=self.device
            )
            
            outputs = self.model(
                **inputs,
                decoder_input_ids=decoder_input_ids,
                output_hidden_states=True
            )
            
            # Use the last hidden state of the encoder as embeddings
            embeddings = outputs.encoder_last_hidden_state.mean(dim=1).cpu().numpy()
            
            # Normalize the vector
            normalized_embedding = embeddings[0] / np.linalg.norm(embeddings[0])
            return normalized_embedding

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
    """Fetches rules, generates embeddings using CodeT5, and stores them in the database."""
    embedder = CodeEmbedder()
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
                embedding = embedder.get_embedding(combined_text)
                
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
    """Generate embedding for SQL code using the same CodeT5 model."""
    embedder = CodeEmbedder()
    return embedder.get_embedding(sql_code)

if __name__ == "__main__":
    vectorize_rules()
