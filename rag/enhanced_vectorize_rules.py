import psycopg2
import sys
import os
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
import re

# Set project root and add it to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from config import DB_CONFIG
from rag.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

def extract_sql_patterns(code_pattern: str, example_snippet: str) -> str:
    """Extract SQL-like patterns from regex and examples for better matching."""
    sql_keywords = []
    
    # Extract SQL keywords from regex pattern
    if code_pattern:
        # Remove regex symbols and extract SQL keywords
        cleaned_pattern = re.sub(r'[\\(){}[\].*+?^$|]', ' ', code_pattern)
        cleaned_pattern = re.sub(r'\\[a-z]+', ' ', cleaned_pattern)  # Remove \s, \w, etc.
        words = cleaned_pattern.split()
        
        # Filter for SQL keywords
        sql_keywords.extend([word.upper() for word in words 
                           if word.upper() in ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 
                                             'GROUP', 'ORDER', 'BY', 'HAVING', 'INSERT', 'UPDATE', 'DELETE',
                                             'CREATE', 'ALTER', 'DROP', 'INDEX', 'TABLE', 'VIEW', 'GRANT',
                                             'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT', 'LIMIT', 'TOP',
                                             'EXISTS', 'IN', 'LIKE', 'BETWEEN', 'AND', 'OR', 'NOT']])
    
    # Extract SQL from example snippet
    example_sql = ""
    if example_snippet:
        # Remove comments and clean up
        lines = example_snippet.split('\n')
        sql_lines = [line.strip() for line in lines if not line.strip().startswith('--')]
        example_sql = ' '.join(sql_lines)
    
    return f"{' '.join(sql_keywords)} {example_sql}".strip()

def create_semantic_description(title: str, description: str, category: str, practice_type: str) -> str:
    """Create a semantic description focusing on SQL concepts."""
    intent_words = []
    
    # Map categories to semantic concepts
    category_mapping = {
        'Performance': 'slow query optimization speed efficiency index',
        'Security': 'injection vulnerability privilege access permission',
        'Data Integrity': 'constraint validation consistency transaction',
        'Clarity': 'readable maintainable naming convention alias',
        'Maintainability': 'reusable modular documentation consistent'
    }
    
    intent_words.extend(category_mapping.get(category, '').split())
    
    # Add practice type context
    if practice_type == 'bad':
        intent_words.extend(['avoid', 'prevent', 'problematic', 'issue'])
    else:
        intent_words.extend(['use', 'implement', 'best practice', 'recommended'])
    
    # Extract key concepts from title and description
    key_terms = re.findall(r'\b[A-Z]{2,}|[A-Z][a-z]+\s*[A-Z][a-z]+|\b(?:SQL|query|table|column|index|join|subquery)\b', 
                          f"{title} {description}", re.IGNORECASE)
    
    return f"{title} {description} {' '.join(intent_words)} {' '.join(key_terms)}"

def enhanced_combine_rule_text(rule: Dict[str, Any]) -> Tuple[str, str, str]:
    """Create multiple specialized embeddings for better matching."""
    
    # 1. SQL-focused embedding (for structural matching)
    sql_pattern_text = extract_sql_patterns(rule.get('code_pattern', ''), rule.get('example_snippet', ''))
    
    # 2. Semantic intent embedding (for conceptual matching)
    semantic_text = create_semantic_description(
        rule.get('title', ''),
        rule.get('description', ''),
        rule.get('category', ''),
        rule.get('practice_type', 'bad')
    )
    
    # 3. Combined hybrid embedding
    hybrid_text = f"SQL Pattern: {sql_pattern_text} Intent: {semantic_text}"
    
    return sql_pattern_text, semantic_text, hybrid_text

def enhanced_vectorize_rules():
    """Enhanced vectorization with multiple embedding approaches."""
    embedding_service = get_embedding_service()
    conn = None
    
    try:
        logger.info("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Add new vector columns if they don't exist
        try:
            cur.execute("""
                ALTER TABLE rules 
                ADD COLUMN IF NOT EXISTS sql_pattern_vector FLOAT[],
                ADD COLUMN IF NOT EXISTS semantic_vector FLOAT[],
                ADD COLUMN IF NOT EXISTS hybrid_vector FLOAT[];
            """)
            conn.commit()
        except Exception as e:
            logger.warning(f"Could not add new columns (might already exist): {e}")
            conn.rollback()

        # Fetch rules that need enhanced vectorization
        cur.execute("""
            SELECT id, title, description, category, code_pattern, example_snippet, practice_type
            FROM rules 
            WHERE sql_pattern_vector IS NULL OR semantic_vector IS NULL OR hybrid_vector IS NULL;
        """)
        rules = cur.fetchall()

        if not rules:
            logger.info("All rules are already vectorized with enhanced method.")
            return

        logger.info(f"Found {len(rules)} rules to enhance vectorization...")

        for rule in rules:
            rule_dict = {
                'id': rule[0],
                'title': rule[1],
                'description': rule[2],
                'category': rule[3],
                'code_pattern': rule[4],
                'example_snippet': rule[5],
                'practice_type': rule[6]
            }
            
            try:
                # Generate specialized embeddings
                sql_pattern_text, semantic_text, hybrid_text = enhanced_combine_rule_text(rule_dict)
                
                sql_embedding = embedding_service.get_embedding(sql_pattern_text) if sql_pattern_text else None
                semantic_embedding = embedding_service.get_embedding(semantic_text)
                hybrid_embedding = embedding_service.get_embedding(hybrid_text)
                
                # Update the database
                cur.execute("""
                    UPDATE rules SET 
                        sql_pattern_vector = %s,
                        semantic_vector = %s,
                        hybrid_vector = %s,
                        last_updated_utc = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (
                    sql_embedding.tolist() if sql_embedding is not None else None,
                    semantic_embedding.tolist(),
                    hybrid_embedding.tolist(),
                    rule_dict['id']
                ))
                conn.commit()
                logger.info(f"Enhanced vectorization for rule {rule_dict['id']}: {rule_dict['title']}")
                
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

# Code chunk enhancement functions
def enhance_sql_code_for_matching(sql_code: str) -> Tuple[str, str, str]:
    """Enhance SQL code for better semantic matching."""
    
    # 1. Structural enhancement: Extract SQL patterns
    sql_structure = extract_sql_structure(sql_code)
    
    # 2. Semantic enhancement: Add context about intent
    sql_intent = infer_sql_intent(sql_code)
    
    # 3. Hybrid: Combine both
    hybrid_text = f"SQL Structure: {sql_structure} Intent: {sql_intent} Original: {sql_code}"
    
    return sql_structure, sql_intent, hybrid_text

def extract_sql_structure(sql_code: str) -> str:
    """Extract structural patterns from SQL code."""
    structure_elements = []
    
    # Normalize the code
    normalized = re.sub(r'\s+', ' ', sql_code.upper().strip())
    
    # Extract main SQL keywords
    main_keywords = re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|GRANT|REVOKE)\b', normalized)
    if main_keywords:
        structure_elements.append(f"Operation: {main_keywords[0]}")
    
    # Extract table patterns
    table_patterns = re.findall(r'FROM\s+(\w+(?:\s+\w+)?(?:\s*,\s*\w+(?:\s+\w+)?)*)', normalized)
    if table_patterns:
        structure_elements.append(f"Tables: {table_patterns[0]}")
    
    # Extract JOIN patterns
    join_patterns = re.findall(r'((?:INNER|LEFT|RIGHT|FULL|OUTER)?\s*JOIN\s+\w+)', normalized)
    if join_patterns:
        structure_elements.append(f"Joins: {' '.join(join_patterns)}")
    
    # Extract WHERE conditions
    if 'WHERE' in normalized:
        structure_elements.append("Has WHERE clause")
    
    # Extract other important elements
    if 'GROUP BY' in normalized:
        structure_elements.append("Has GROUP BY")
    if 'ORDER BY' in normalized:
        structure_elements.append("Has ORDER BY")
    if 'HAVING' in normalized:
        structure_elements.append("Has HAVING")
    if 'DISTINCT' in normalized:
        structure_elements.append("Uses DISTINCT")
    if re.search(r'SELECT\s+\*', normalized):
        structure_elements.append("Uses SELECT *")
    
    return ' '.join(structure_elements)

def infer_sql_intent(sql_code: str) -> str:
    """Infer the intent/purpose of SQL code for semantic matching."""
    intent_indicators = []
    normalized = sql_code.upper()
    
    # Detect potential issues
    if re.search(r'SELECT\s+\*', normalized):
        intent_indicators.append("broad selection performance concern")
    
    if re.search(r'WHERE.*LIKE.*%.*%', normalized):
        intent_indicators.append("pattern matching performance impact")
    
    if 'COUNT(*)' in normalized:
        intent_indicators.append("counting optimization opportunity")
    
    if re.search(r'WHERE.*OR.*OR', normalized):
        intent_indicators.append("multiple OR conditions index usage")
    
    if re.search(r'IN\s*\(\s*SELECT', normalized):
        intent_indicators.append("subquery performance consideration")
    
    if 'GRANT ALL' in normalized:
        intent_indicators.append("security privilege escalation")
    
    if 'EXECUTE' in normalized and '+' in sql_code:
        intent_indicators.append("dynamic SQL injection risk")
    
    if re.search(r'FROM\s+\w+\s*,\s*\w+', normalized) and 'JOIN' not in normalized:
        intent_indicators.append("implicit join cartesian product risk")
    
    # Detect good practices
    if 'EXISTS' in normalized:
        intent_indicators.append("efficient existence check")
    
    if 'LIMIT' in normalized or 'TOP' in normalized:
        intent_indicators.append("result set limitation")
    
    if 'FOREIGN KEY' in normalized:
        intent_indicators.append("referential integrity")
    
    if 'CHECK' in normalized and 'CONSTRAINT' in normalized:
        intent_indicators.append("data validation")
    
    return ' '.join(intent_indicators) if intent_indicators else "general SQL operation"

if __name__ == "__main__":
    enhanced_vectorize_rules()
