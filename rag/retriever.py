import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import sys
import os
from typing import Dict, List, Tuple, Optional

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG
from .ai_analyzer import get_ai_suggestions

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

def find_regex_matches(code_chunk: str, cur, language: str) -> List[Dict]:
    """Find rules that match the code chunk using regex patterns."""
    matched_rules = []
    
    cur.execute(
        "SELECT id, title, description, code_pattern, severity, practice_type, category "
        "FROM rules WHERE language = %s AND code_pattern IS NOT NULL;",
        (language,)
    )
    rules = cur.fetchall()

    for rule_id, title, description, code_pattern, severity, practice_type, category in rules:
        if re.search(code_pattern, code_chunk, re.IGNORECASE):
            matched_rules.append({
                'id': rule_id,
                'title': title,
                'description': description,
                'severity': severity,
                'practice_type': practice_type,
                'category': category,
                'match_type': 'regex',
                'confidence': 1.0  # Regex matches are considered highest confidence
            })
    
    return matched_rules

def find_semantic_matches(code_chunk: str, cur, language: str, similarity_threshold: float = 0.55) -> List[Dict]:
    """Find rules that match the code chunk using semantic similarity."""
    semantic_matches = []
    
    code_embedding = model.encode(code_chunk, convert_to_tensor=False)
    cur.execute(
        "SELECT id, title, description, severity, practice_type, category, vector "
        "FROM rules WHERE language = %s AND vector IS NOT NULL;",
        (language,)
    )
    rules = cur.fetchall()

    for rule_id, title, description, severity, practice_type, category, vector in rules:
        if vector:
            similarity = np.dot(code_embedding, np.array(vector)) / (
                np.linalg.norm(code_embedding) * np.linalg.norm(np.array(vector))
            )
            if similarity > similarity_threshold:
                semantic_matches.append({
                    'id': rule_id,
                    'title': title,
                    'description': description,
                    'severity': severity,
                    'practice_type': practice_type,
                    'category': category,
                    'match_type': 'semantic',
                    'confidence': float(similarity)
                })
    
    return semantic_matches

def combine_and_rank_matches(regex_matches: List[Dict], semantic_matches: List[Dict], top_k: int = 3) -> List[Dict]:
    """Combine and rank matches from both regex and semantic search."""
    # Start with regex matches (they have highest confidence)
    combined_matches = regex_matches.copy()
    
    # Add semantic matches that don't overlap with regex matches
    seen_rule_ids = {rule['id'] for rule in regex_matches}
    
    for semantic_match in semantic_matches:
        if semantic_match['id'] not in seen_rule_ids:
            combined_matches.append(semantic_match)
            seen_rule_ids.add(semantic_match['id'])
    
    # Sort by confidence score
    combined_matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    return combined_matches[:top_k]

def find_relevant_rules(code_chunk: str, language: str = 'SQL', top_k: int = 3, 
                       similarity_threshold: float = 0.55) -> Tuple[Dict[str, List], str]:
    """
    Find relevant rules using regex and semantic matching.
    
    Args:
        code_chunk: The code to analyze
        language: Programming language ('SQL' or 'PySpark')
        top_k: Maximum number of rules to return
        similarity_threshold: Minimum similarity score for semantic matches
    
    Returns:
        Tuple of (relevant_rules dict, method_used string)
    """
    conn = None
    relevant_rules = {'good_practices': [], 'bad_practices': []}
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Get matches from both approaches
        print(f"\nAnalyzing code chunk using hybrid approach...\n---\n{code_chunk[:200]}...\n---")
        
        regex_matches = find_regex_matches(code_chunk, cur, language)
        semantic_matches = find_semantic_matches(code_chunk, cur, language, similarity_threshold)
        
        # 2. Combine and rank the matches
        combined_matches = combine_and_rank_matches(regex_matches, semantic_matches, top_k)
        
        # 3. Organize results by practice type
        for match in combined_matches:
            if match['practice_type'] == 'bad':
                relevant_rules['bad_practices'].append(match)
            else:
                relevant_rules['good_practices'].append(match)
        
        # 4. Determine the method used - this will affect the prompt in generator.py
        if regex_matches and semantic_matches:
            method = "Hybrid Match"
        elif regex_matches:
            method = "Regex Match"
        elif semantic_matches:
            method = "Vector Search"  # Keep this name to match generator.py's logic
        else:
            method = "No Matches"  # This will trigger the creative AI analysis in generator.py
            
        match_counts = {
            'regex': len(regex_matches),
            'semantic': len(semantic_matches),
            'combined': len(combined_matches)
        }
        print(f"Found {match_counts['regex']} regex matches and {match_counts['semantic']} semantic matches.")
        print(f"After combining and ranking: {match_counts['combined']} total matches.")
        
        return relevant_rules, method

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return relevant_rules, "Error"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return relevant_rules, "Error"
    finally:
        if conn is not None:
            conn.close()
