import psycopg2
import re
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import DB_CONFIG

def get_all_rules_for_language(language):
    """Retrieves all rules for a given language from the database."""
    conn = connect_db()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cur:
            # Corrected the query to use the correct column names: 'title' and 'category'
            cur.execute("SELECT id, title, description, code_pattern, severity, practice_type, category FROM rules WHERE language = %s", (language,))
            rules_data = cur.fetchall()
            rules = [
                {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'code_pattern': row[3],
                    'severity': row[4],
                    'practice_type': row[5],
                    'category': row[6]
                }
                for row in rules_data
            ]
            return rules
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def find_relevant_rules(code_chunk, all_rules):
    """Finds relevant rules, with strict prioritization for critical issues."""
    matched_rules = []

    # 1. Find all matching bad practice rules
    for rule in all_rules:
        if rule['practice_type'] == 'bad':
            if re.search(rule['code_pattern'], code_chunk, re.IGNORECASE):
                matched_rules.append(rule)

    # 2. Prioritize critical rules. If any are found, discard all others.
    critical_rules = [rule for rule in matched_rules if rule.get('severity') == 'Critical']
    if critical_rules:
        return {'good_practices': [], 'bad_practices': critical_rules}

    # 3. If no critical rules, but other bad practices exist, return them.
    if matched_rules:
        return {'good_practices': [], 'bad_practices': matched_rules}

    # 4. If no bad practices are found, find relevant good practices for context.
    good_practices = []
    for rule in all_rules:
        if rule['practice_type'] == 'good':
            command = rule['code_pattern'].lower()
            if command in code_chunk.lower():
                good_practices.append(rule)

    return {'good_practices': good_practices, 'bad_practices': []}

def connect_db():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None
