import psycopg2
import numpy as np
import sys
import os
import logging
from typing import Dict, List, Tuple, Optional
from .vectorize_rules import CodeEmbedder, vectorize_sql_code

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    
    # Use the same CodeT5 model for code embedding
    code_embedding = vectorize_sql_code(code_chunk)
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
                       similarity_threshold: float = 0.65) -> Tuple[Dict[str, List], str]:
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
    matched_bad_rules = []

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

        for rule_id, title, description, code_pattern, severity, _, category in bad_practice_rules:
            if re.search(code_pattern, code_chunk, re.IGNORECASE):
                matched_bad_rules.append({
                    'id': rule_id, 'title': title, 'description': description, 
                    'severity': severity, 'practice_type': 'bad', 'category': category
                })
        
        # If any regex matches were found, add them to the list. The process will continue to the vector search.
        if matched_bad_rules:
            print(f"Found {len(matched_bad_rules)} direct violation(s) via regex.")
            relevant_rules['bad_practices'].extend(matched_bad_rules)
            # Do not return here; continue to vector search to find other potential issues.

        # 2. Always proceed to vector search for additional semantic relevance
        print("Proceeding to vector similarity search for additional rules...")
        code_embedding = model.encode(code_chunk, convert_to_tensor=False)
        cur.execute(
            "SELECT id, title, description, severity, practice_type, category, vector FROM rules WHERE language = %s AND vector IS NOT NULL;",
            (language,)
        )
        rules_data = cur.fetchall()
        
        if not rules_data:
            print("No vectorized rules found.")
            # If regex found something, we can still return that.
            log_method = "Regex Match" if matched_bad_rules else "Vector Search"
            return relevant_rules, log_method

        rule_similarities = []
        for rule in rules_data:
            rule_id, title, description, severity, practice_type, category, vector = rule
            if vector:
                # Avoid adding duplicate rules if found by both regex and vector search
                if any(r['id'] == rule_id for r in relevant_rules['bad_practices']):
                    continue

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
        
        # Determine the log method based on what was found
        log_method = "Hybrid Search" if matched_bad_rules and top_rules else ("Regex Match" if matched_bad_rules else "Vector Search")

        return relevant_rules, log_method

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return {'good_practices': [], 'bad_practices': []}, "Error"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {'good_practices': [], 'bad_practices': []}, "Error"
    finally:
        if conn:
            conn.close()
