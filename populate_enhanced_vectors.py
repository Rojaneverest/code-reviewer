#!/usr/bin/env python3
"""
Script to populate the database with enhanced vectors for all rules.
"""

import psycopg2
import sys
import os
import logging
from typing import List, Tuple, Optional

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG
from rag.embedding_service import get_embedding_service
from rag.enhanced_vectorize_rules import enhanced_combine_rule_text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def populate_enhanced_vectors():
    """Populate all rules with enhanced vector embeddings."""
    conn = None
    try:
        # Connect to database
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get embedding service
        embedding_service = get_embedding_service()
        logger.info("Embedding service initialized")
        
        # Fetch all rules
        cursor.execute("""
        SELECT id, title, description, code_pattern, example_snippet, category, severity, practice_type 
        FROM rules 
        ORDER BY id;
        """)
        
        rules = cursor.fetchall()
        logger.info(f"Found {len(rules)} rules to process")
        
        processed_count = 0
        error_count = 0
        
        for rule in rules:
            rule_id, title, description, code_pattern, example_snippet, category, severity, practice_type = rule
            
            try:
                logger.info(f"Processing rule {rule_id}: {title}")
                
                # Create rule dictionary for the enhanced function
                rule_dict = {
                    'title': title,
                    'description': description,
                    'code_pattern': code_pattern,
                    'example_snippet': example_snippet,
                    'category': category,
                    'practice_type': practice_type
                }
                
                # Generate enhanced embeddings
                sql_pattern_text, semantic_intent_text, hybrid_text = enhanced_combine_rule_text(
                    rule_dict
                )
                
                # Create three specialized vectors
                sql_vector = embedding_service.get_embedding(sql_pattern_text)
                semantic_vector = embedding_service.get_embedding(semantic_intent_text)
                hybrid_vector = embedding_service.get_embedding(hybrid_text)
                
                # Convert to lists for PostgreSQL
                sql_vector_list = sql_vector.tolist() if sql_vector is not None else None
                semantic_vector_list = semantic_vector.tolist() if semantic_vector is not None else None
                hybrid_vector_list = hybrid_vector.tolist() if hybrid_vector is not None else None
                
                # Update the rule with all vectors
                cursor.execute("""
                UPDATE rules 
                SET sql_pattern_vector = %s, 
                    semantic_intent_vector = %s, 
                    hybrid_vector = %s 
                WHERE id = %s;
                """, (sql_vector_list, semantic_vector_list, hybrid_vector_list, rule_id))
                
                processed_count += 1
                logger.info(f"  ✓ Updated vectors for rule {rule_id}")
                
                # Log vector info
                logger.debug(f"    SQL pattern text: {sql_pattern_text[:100] if sql_pattern_text else 'None'}...")
                logger.debug(f"    Semantic text: {semantic_intent_text[:100] if semantic_intent_text else 'None'}...")
                logger.debug(f"    Hybrid text: {hybrid_text[:100] if hybrid_text else 'None'}...")
                
            except Exception as e:
                logger.error(f"Error processing rule {rule_id}: {e}")
                error_count += 1
                continue
        
        # Commit all changes
        conn.commit()
        
        logger.info(f"\n=== VECTORIZATION COMPLETE ===")
        logger.info(f"Total rules processed: {processed_count}")
        logger.info(f"Errors encountered: {error_count}")
        
        # Verify the updates
        cursor.execute("""
        SELECT 
            COUNT(*) as total_rules,
            COUNT(vector) as original_vectors,
            COUNT(sql_pattern_vector) as sql_pattern_vectors,
            COUNT(semantic_vector) as semantic_vectors,
            COUNT(hybrid_vector) as hybrid_vectors
        FROM rules;
        """)
        
        counts = cursor.fetchone()
        logger.info(f"\nVector population summary:")
        logger.info(f"  Total rules: {counts[0]}")
        logger.info(f"  Original vectors: {counts[1]}")
        logger.info(f"  SQL pattern vectors: {counts[2]}")
        logger.info(f"  Semantic vectors: {counts[3]}")
        logger.info(f"  Hybrid vectors: {counts[4]}")
        
        # Show sample of vector dimensions
        cursor.execute("""
        SELECT title, 
               array_length(vector, 1) as orig_dim,
               array_length(sql_pattern_vector, 1) as sql_dim,
               array_length(semantic_vector, 1) as sem_dim,
               array_length(hybrid_vector, 1) as hyb_dim
        FROM rules 
        WHERE vector IS NOT NULL 
        LIMIT 3;
        """)
        
        samples = cursor.fetchall()
        logger.info(f"\nSample vector dimensions:")
        for title, orig_dim, sql_dim, sem_dim, hyb_dim in samples:
            logger.info(f"  {title}: orig={orig_dim}, sql={sql_dim}, sem={sem_dim}, hyb={hyb_dim}")
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        logger.error(f"General error: {e}")
    finally:
        if conn:
            conn.close()

def check_vector_status():
    """Check the current status of vectors in the database."""
    conn = None
    try:
        logger.info("Checking vector status...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'rules' AND column_name LIKE '%vector%'
        ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        logger.info(f"Vector columns found: {[col[0] for col in columns]}")
        
        # Check vector population
        cursor.execute("""
        SELECT 
            COUNT(*) as total_rules,
            COUNT(vector) as original_vectors,
            COUNT(sql_pattern_vector) as sql_pattern_vectors,
            COUNT(semantic_vector) as semantic_vectors,
            COUNT(hybrid_vector) as hybrid_vectors
        FROM rules;
        """)
        
        counts = cursor.fetchone()
        logger.info(f"Vector population status:")
        logger.info(f"  Total rules: {counts[0]}")
        logger.info(f"  Original vectors: {counts[1]}")
        logger.info(f"  SQL pattern vectors: {counts[2]}")
        logger.info(f"  Semantic vectors: {counts[3]}")
        logger.info(f"  Hybrid vectors: {counts[4]}")
        
    except Exception as e:
        logger.error(f"Error checking vector status: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_vector_status()
    else:
        populate_enhanced_vectors()
