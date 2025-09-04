#!/usr/bin/env python3
"""
Thorough testing script for semantic-based matching.
This script analyzes exactly which rules are being fetched for each code chunk.
"""

import sys
import os
import logging
import json
from typing import Dict, List, Tuple
import numpy as np

# Add project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from rag.embedding_service import get_embedding_service
from rag.retriever import _find_semantic_matches
from utils.line_mapper import map_sql_statements_to_lines
from config import DB_CONFIG
import psycopg2

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SemanticTestAnalyzer:
    """Comprehensive analyzer for semantic matching behavior."""
    
    def __init__(self, verbose=True):
        self.embedding_service = get_embedding_service()
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.verbose = verbose
        
    def get_all_rules(self) -> List[Dict]:
        """Get all rules from the database with their embeddings."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title, description, code_pattern, severity, category, 
                   practice_type, vector, array_length(vector, 1) as vector_length
            FROM rules 
            WHERE language = 'SQL'
            ORDER BY id;
        """)
        
        rules = []
        for row in cursor.fetchall():
            rules.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'code_pattern': row[3],
                'severity': row[4],
                'category': row[5],
                'practice_type': row[6],
                'vector': row[7],
                'vector_length': row[8],
                'has_vector': row[7] is not None
            })
        
        return rules
    
    def calculate_similarity_with_all_rules(self, code_chunk: str, rules: List[Dict]) -> List[Dict]:
        """Calculate similarity between code chunk and all rules."""
        try:
            # Get embedding for the code chunk
            query_embedding = self.embedding_service.get_embedding(code_chunk)
            
            similarities = []
            for rule in rules:
                if rule['vector']:
                    rule_embedding = np.array(rule['vector'])
                    similarity = np.dot(query_embedding, rule_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(rule_embedding)
                    )
                    
                    similarities.append({
                        'rule_id': rule['id'],
                        'title': rule['title'],
                        'description': rule['description'],
                        'code_pattern': rule['code_pattern'],
                        'severity': rule['severity'],
                        'category': rule['category'],
                        'practice_type': rule['practice_type'],
                        'similarity': float(similarity),
                        'meets_threshold_0_7': similarity > 0.7,
                        'meets_threshold_0_8': similarity > 0.8,
                        'meets_threshold_0_75': similarity > 0.75
                    })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities
            
        except Exception as e:
            logger.error(f"Error calculating similarities: {e}")
            return []
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a file and return detailed semantic matching results."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Get all rules
        all_rules = self.get_all_rules()
        rules_with_vectors = [r for r in all_rules if r['has_vector']]
        
        print(f"\n{'='*80}")
        print(f"SEMANTIC ANALYSIS FOR: {file_path}")
        print(f"{'='*80}")
        print(f"Total rules in database: {len(all_rules)}")
        print(f"Rules with vectors: {len(rules_with_vectors)}")
        print(f"Rules without vectors: {len(all_rules) - len(rules_with_vectors)}")
        
        # Split into chunks using the same method as main.py
        chunks_with_lines = map_sql_statements_to_lines(content)
        chunks = [chunk_data[0] for chunk_data in chunks_with_lines]  # Extract just the code
        print(f"Number of chunks: {len(chunks)}")
        
        analysis_results = {
            'file_path': file_path,
            'total_rules': len(all_rules),
            'rules_with_vectors': len(rules_with_vectors),
            'total_chunks': len(chunks),
            'chunk_analyses': []
        }
        
        for i, (chunk, start_line) in enumerate(chunks_with_lines, 1):
            print(f"\n{'-'*60}")
            print(f"CHUNK {i}")
            print(f"{'-'*60}")
            
            # Calculate end line
            chunk_lines = chunk.strip().split('\n')
            end_line = start_line + len(chunk_lines) - 1
            
            print(f"Lines {start_line}-{end_line}:")
            if self.verbose:
                print(f"```sql")
                print(chunk.strip())
                print(f"```")
            else:
                # Show just the first line for concise output
                first_line = chunk.strip().split('\n')[0]
                print(f"Code: {first_line}...")
            
            # Calculate similarities with all rules
            similarities = self.calculate_similarity_with_all_rules(chunk, rules_with_vectors)
            
            # Analyze thresholds
            threshold_analysis = {
                '0.7': [s for s in similarities if s['meets_threshold_0_7']],
                '0.75': [s for s in similarities if s['meets_threshold_0_75']],
                '0.8': [s for s in similarities if s['meets_threshold_0_8']]
            }
            
            print(f"\nSIMILARITY ANALYSIS:")
            print(f"  Rules above 0.7 threshold: {len(threshold_analysis['0.7'])}")
            print(f"  Rules above 0.75 threshold: {len(threshold_analysis['0.75'])}")
            print(f"  Rules above 0.8 threshold: {len(threshold_analysis['0.8'])}")
            
            print(f"\nTOP 3 MOST SIMILAR RULES:")
            for j, sim in enumerate(similarities[:3], 1):
                status = "✅" if sim['meets_threshold_0_7'] else "❌"
                print(f"  {j}. {status} [{sim['similarity']:.3f}] Rule {sim['rule_id']}: {sim['title']}")
                if self.verbose:
                    print(f"     Category: {sim['category']} | Severity: {sim['severity']}")
                    print(f"     Pattern: {sim['code_pattern'][:40]}...")
                print()
            
            # Test actual retriever function using database cursor
            cursor = self.conn.cursor()
            print(f"ACTUAL RETRIEVER RESULTS:")
            actual_matches = _find_semantic_matches(chunk, cursor, 'SQL', 0.7)
            print(f"  Retriever returned {len(actual_matches)} matches")
            for match in actual_matches:
                print(f"  - Rule {match['id']}: {match['title']} (Confidence: {match.get('confidence', 'N/A')})")
            cursor.close()
            
            chunk_analysis = {
                'chunk_number': i,
                'start_line': start_line,
                'end_line': end_line,
                'code': chunk.strip(),
                'top_similarities': similarities[:3],
                'threshold_counts': {
                    '0.7': len(threshold_analysis['0.7']),
                    '0.75': len(threshold_analysis['0.75']),
                    '0.8': len(threshold_analysis['0.8'])
                },
                'actual_retriever_matches': len(actual_matches)
            }
            
            analysis_results['chunk_analyses'].append(chunk_analysis)
        
        return analysis_results
    
    def save_analysis_report(self, analysis: Dict, output_file: str):
        """Save the analysis report to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"\nDetailed analysis saved to: {output_file}")
    
    def run_comprehensive_test(self, test_files: List[str]):
        """Run comprehensive semantic analysis on multiple test files."""
        for file_path in test_files:
            if os.path.exists(file_path):
                analysis = self.analyze_file(file_path)
                
                # Save individual report
                base_name = os.path.basename(file_path).replace('.sql', '')
                output_file = f"outputs/semantic_analysis_{base_name}.json"
                self.save_analysis_report(analysis, output_file)
            else:
                print(f"Warning: File not found: {file_path}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

def main():
    """Main function to run semantic analysis tests."""
    
    test_files = [
        'test_files/semantic_test.sql',
        'test_files/test_code_full.sql',
        'test_files/beast.sql'
    ]
    
    # Set verbose=False for more concise output, verbose=True for detailed output
    analyzer = SemanticTestAnalyzer(verbose=False)
    
    try:
        print("Starting comprehensive semantic matching analysis...")
        analyzer.run_comprehensive_test(test_files)
        
        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print("Check the outputs/ directory for detailed JSON reports.")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
