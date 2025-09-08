import psycopg2
import numpy as np
import sys
import os
import logging
from typing import Dict, List, Tuple
from .enhanced_vectorize_rules import enhance_sql_code_for_matching

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG, SEMANTIC_CONFIG
from rag.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

def _find_enhanced_semantic_matches(code_chunk: str, cur, language: str, similarity_threshold: float) -> List[Dict]:
    """Enhanced semantic matching using multiple vector approaches."""
    embedding_service = get_embedding_service()
    
    # Enhance the code chunk for better matching
    sql_structure, sql_intent, hybrid_text = enhance_sql_code_for_matching(code_chunk)
    
    # Generate embeddings for different aspects
    code_structure_embedding = embedding_service.get_embedding(sql_structure) if sql_structure else None
    code_intent_embedding = embedding_service.get_embedding(sql_intent) if sql_intent else None
    code_hybrid_embedding = embedding_service.get_embedding(hybrid_text)
    code_original_embedding = embedding_service.get_embedding(code_chunk)
    
    # Fetch rules with all vector types
    cur.execute("""
        SELECT id, title, description, severity, practice_type, category, 
               vector, sql_pattern_vector, semantic_vector, hybrid_vector
        FROM rules 
        WHERE language = %s 
        AND (vector IS NOT NULL OR sql_pattern_vector IS NOT NULL 
             OR semantic_vector IS NOT NULL OR hybrid_vector IS NOT NULL);
    """, (language,))
    
    rules = cur.fetchall()
    semantic_matches = []
    
    for rule in rules:
        rule_id, title, description, severity, practice_type, category, \
        original_vector, sql_pattern_vector, semantic_vector, hybrid_vector = rule
        
        similarities = []
        match_types = []
        
        # 1. Original embedding similarity (backward compatibility)
        if original_vector and code_original_embedding is not None:
            sim = cosine_similarity(code_original_embedding, np.array(original_vector))
            similarities.append(sim)
            match_types.append('original')
        
        # 2. SQL Pattern similarity (structural matching)
        if sql_pattern_vector and code_structure_embedding is not None:
            sim = cosine_similarity(code_structure_embedding, np.array(sql_pattern_vector))
            similarities.append(sim * 1.2)  # Boost structural matches
            match_types.append('sql_pattern')
        
        # 3. Semantic intent similarity (conceptual matching)
        if semantic_vector and code_intent_embedding is not None:
            sim = cosine_similarity(code_intent_embedding, np.array(semantic_vector))
            similarities.append(sim * 1.1)  # Slight boost for intent matches
            match_types.append('semantic_intent')
        
        # 4. Hybrid similarity (comprehensive matching)
        if hybrid_vector and code_hybrid_embedding is not None:
            sim = cosine_similarity(code_hybrid_embedding, np.array(hybrid_vector))
            similarities.append(sim)
            match_types.append('hybrid')
        
        if similarities:
            # Use the maximum similarity across all approaches
            best_similarity = max(similarities)
            best_match_type = match_types[similarities.index(max(similarities))]
            
            # Apply threshold
            if best_similarity > similarity_threshold:
                semantic_matches.append({
                    'id': rule_id,
                    'title': title,
                    'description': description,
                    'severity': severity,
                    'practice_type': practice_type,
                    'category': category,
                    'match_type': f'enhanced_semantic_{best_match_type}',
                    'confidence': float(best_similarity),
                    'all_similarities': {mt: sim for mt, sim in zip(match_types, similarities)}
                })
    
    return semantic_matches

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def find_relevant_rules_enhanced(code_chunk: str, language: str = 'SQL', top_k: int = None, 
                               similarity_threshold: float = None) -> Tuple[Dict[str, List], str]:
    """
    Enhanced rule finding using multiple vectorization approaches.
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

        logger.info(f"Analyzing code chunk using enhanced hybrid approach...")
        
        # Get regex matches (unchanged)
        regex_matches = _find_regex_matches(code_chunk, cur, language)
        
        # Get enhanced semantic matches
        semantic_matches = _find_enhanced_semantic_matches(code_chunk, cur, language, similarity_threshold)
        
        # Combine and rank the matches
        combined_matches = _combine_and_rank_matches(regex_matches, semantic_matches, top_k)
        
        # Organize results by practice type
        for match in combined_matches:
            if match['practice_type'] == 'bad':
                relevant_rules['bad_practices'].append(match)
            else:
                relevant_rules['good_practices'].append(match)
        
        # Determine the method used
        if regex_matches and semantic_matches:
            method = "Enhanced Hybrid Match"
        elif regex_matches:
            method = "Regex Match"
        elif semantic_matches:
            method = "Enhanced Vector Search"
        else:
            method = "No Matches"
            
        match_counts = {
            'regex': len(regex_matches),
            'semantic': len(semantic_matches),
            'combined': len(combined_matches)
        }
        logger.info(f"Enhanced analysis: {match_counts['regex']} regex, {match_counts['semantic']} semantic, {match_counts['combined']} total matches.")
        
        return relevant_rules, method

    except Exception as e:
        logger.warning(f"Enhanced analysis failed: {e}")
        logger.info("Falling back to original analysis method")
        # Fallback to original method
        from .retriever import find_relevant_rules
        return find_relevant_rules(code_chunk, language, top_k, similarity_threshold)
    finally:
        if conn:
            conn.close()

# Import the original functions we still need
def _find_regex_matches(code_chunk: str, cur, language: str) -> List[Dict]:
    """Find rules that match the code chunk using regex patterns."""
    from .retriever import _find_regex_matches as original_find_regex_matches
    return original_find_regex_matches(code_chunk, cur, language)

def _combine_and_rank_matches(regex_matches: List[Dict], semantic_matches: List[Dict], top_k: int = 6) -> List[Dict]:
    """Combine and rank matches from both regex and semantic search."""
    from .retriever import _combine_and_rank_matches as original_combine_and_rank_matches
    return original_combine_and_rank_matches(regex_matches, semantic_matches, top_k)
