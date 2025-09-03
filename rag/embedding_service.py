import requests
import json
import numpy as np
import os
import sys
import logging
from typing import List, Optional

# Add project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from config import EMBEDDING_CONFIG

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service to handle embeddings using Databricks BGE model only."""
    
    def __init__(self):
        if not EMBEDDING_CONFIG["token"]:
            raise ValueError("DATABRICKS_TOKEN is required but not found in environment variables")
        
        self.config = EMBEDDING_CONFIG
        logger.info("Using Databricks BGE embedding service")
    
    def get_embedding(self, text: str, max_length: int = 512) -> np.ndarray:
        """Generate embedding for given text using Databricks BGE service."""
        return self._get_databricks_embedding(text)
    
    def _get_databricks_embedding(self, text: str) -> np.ndarray:
        """Get embedding from Databricks BGE service."""
        try:
            url = f"{self.config['base_url']}{self.config['endpoint']}"
            
            headers = {
                "Authorization": f"Bearer {self.config['token']}",
                "Content-Type": "application/json"
            }
            
            # BGE model expects input in this format
            payload = {
                "input": [text]
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.config["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract embedding from response
                # BGE typically returns embeddings in 'data' field with 'embedding' key
                if 'data' in result and len(result['data']) > 0:
                    embedding = np.array(result['data'][0]['embedding'])
                    # Normalize the embedding
                    normalized_embedding = embedding / np.linalg.norm(embedding)
                    return normalized_embedding
                else:
                    raise ValueError(f"Unexpected response format: {result}")
            else:
                raise Exception(f"Databricks API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error getting Databricks embedding: {e}")
            raise

# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_embedding(text: str, max_length: int = 512) -> np.ndarray:
    """Convenience function to get embedding using the global service."""
    service = get_embedding_service()
    return service.get_embedding(text, max_length)
