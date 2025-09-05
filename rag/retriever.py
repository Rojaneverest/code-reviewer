import psycopg2
import numpy as np
import sys
import os
import logging
from typing import Dict, List, Tuple
from .vectorize_rules import vectorize_sql_code

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG, SEMANTIC_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import re

def _find_regex_matches(code_chunk: str, cur, language: str) -> List[Dict]:
    """Find rules that match the code chunk using regex patterns."""
    matched_rules = []
    
    cur.execute("""
        SELECT id, title, description, code_pattern, severity, practice_type, category 
        FROM rules 
        WHERE language = %s 
        AND code_pattern IS NOT NULL;
    """, (language,))
    
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
                'confidence': 1.0  # Regex matches have highest confidence
            })
    
    return matched_rules

def _find_semantic_matches(code_chunk: str, cur, language: str, similarity_threshold: float) -> List[Dict]:
    """Find rules that match the code chunk using semantic similarity."""
    code_embedding = vectorize_sql_code(code_chunk)
    
    cur.execute("""
        SELECT id, title, description, severity, practice_type, category, vector 
        FROM rules 
        WHERE language = %s 
        AND vector IS NOT NULL;
    """, (language,))
    
    rules = cur.fetchall()
    semantic_matches = []
    
    for rule in rules:
        rule_id, title, description, severity, practice_type, category, vector = rule
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

def _combine_and_rank_matches(regex_matches: List[Dict], semantic_matches: List[Dict], top_k: int = 6) -> List[Dict]:
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

def find_relevant_rules(code_chunk: str, language: str = 'SQL', top_k: int = None, 
                       similarity_threshold: float = None) -> Tuple[Dict[str, List], str]:
    """
    Find relevant rules using regex and semantic matching.
    
    Args:
        code_chunk: The code to analyze
        language: Programming language ('SQL' or 'PySpark')
        top_k: Maximum number of rules to return (default: 6 from config)
        similarity_threshold: Minimum similarity score for semantic matches (default: 0.65 from config)
    
    Returns:
        Tuple of (relevant_rules dict, method_used string)
    """
    # Use config values if not provided
    if similarity_threshold is None:
        similarity_threshold = SEMANTIC_CONFIG["similarity_threshold"]
    if top_k is None:
        top_k = SEMANTIC_CONFIG["top_k_rules"]
    
    conn = None
    relevant_rules = {'good_practices': [], 'bad_practices': []}
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Get matches from both approaches
        logger.info(f"\nAnalyzing code chunk using hybrid approach...\n---\n{code_chunk[:200]}...\n---")
        
        regex_matches = _find_regex_matches(code_chunk, cur, language)
        semantic_matches = _find_semantic_matches(code_chunk, cur, language, similarity_threshold)
        
        # 2. Combine and rank the matches
        combined_matches = _combine_and_rank_matches(regex_matches, semantic_matches, top_k)
        
        # 3. Organize results by practice type
        for match in combined_matches:
            if match['practice_type'] == 'bad':
                relevant_rules['bad_practices'].append(match)
            else:
                relevant_rules['good_practices'].append(match)
        
        # 4. Determine the method used
        if regex_matches and semantic_matches:
            method = "Hybrid Match"
        elif regex_matches:
            method = "Regex Match"
        elif semantic_matches:
            method = "Vector Search"
        else:
            method = "No Matches"
            
        match_counts = {
            'regex': len(regex_matches),
            'semantic': len(semantic_matches),
            'combined': len(combined_matches)
        }
        logger.info(f"Found {match_counts['regex']} regex matches and {match_counts['semantic']} semantic matches.")
        logger.info(f"After combining and ranking: {match_counts['combined']} total matches.")
        
        return relevant_rules, method

    except psycopg2.Error as e:
        logger.warning(f"Database connection failed: {e}")
        logger.info("Falling back to pure AI analysis - database rules unavailable")
        return {'good_practices': [], 'bad_practices': []}, "Database Unavailable - AI Fallback"
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")
        logger.info("Falling back to pure AI analysis - rule retrieval failed")
        return {'good_practices': [], 'bad_practices': []}, "Rule Retrieval Failed - AI Fallback"
    finally:
        if conn:
            conn.close()
