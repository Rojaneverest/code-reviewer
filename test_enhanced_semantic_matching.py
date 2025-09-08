#!/usr/bin/env python3
"""
Test script to compare original vs enhanced semantic matching.
"""

import os
import sys
import json
import logging
from typing import Dict, List

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from rag.retriever import find_relevant_rules
from rag.enhanced_retriever import find_relevant_rules_enhanced

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_test_sql_files() -> Dict[str, str]:
    """Read all SQL test files for analysis."""
    # Use relative path from script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_files_dir = os.path.join(script_dir, "test_files")
    
    if not os.path.exists(test_files_dir):
        logger.error(f"Test files directory not found: {test_files_dir}")
        return {}
    
    sql_files = {}
    
    try:
        for filename in os.listdir(test_files_dir):
            if filename.endswith('.sql'):
                filepath = os.path.join(test_files_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        sql_files[filename] = f.read()
                        logger.info(f"Read file: {filename}")
                except Exception as e:
                    logger.warning(f"Could not read {filename}: {e}")
    except Exception as e:
        logger.error(f"Error reading directory {test_files_dir}: {e}")
    
    return sql_files

def analyze_code_chunk(chunk: str, filename: str, original_func, enhanced_func):
    """Analyze a code chunk with both methods and compare results."""
    
    # Original method
    try:
        orig_rules, orig_method = original_func(chunk)
        orig_total = len(orig_rules['good_practices']) + len(orig_rules['bad_practices'])
    except Exception as e:
        orig_rules, orig_method = {'good_practices': [], 'bad_practices': []}, f"Error: {e}"
        orig_total = 0
    
    # Enhanced method
    try:
        enh_rules, enh_method = enhanced_func(chunk)
        enh_total = len(enh_rules['good_practices']) + len(enh_rules['bad_practices'])
    except Exception as e:
        enh_rules, enh_method = {'good_practices': [], 'bad_practices': []}, f"Error: {e}"
        enh_total = 0
    
    return {
        'chunk': chunk[:100] + "..." if len(chunk) > 100 else chunk,
        'original': {
            'method': orig_method,
            'total_matches': orig_total,
            'rules': orig_rules
        },
        'enhanced': {
            'method': enh_method,
            'total_matches': enh_total,
            'rules': enh_rules
        }
    }

def get_similarity_info(rules: Dict[str, List]) -> List[float]:
    """Extract similarity scores from rule matches."""
    similarities = []
    for practice_type in ['good_practices', 'bad_practices']:
        for rule in rules.get(practice_type, []):
            if 'confidence' in rule:
                similarities.append(rule['confidence'])
            elif 'match_score' in rule:
                similarities.append(rule['match_score'])
    return similarities

def chunk_sql_content(content: str, chunk_size: int = 200) -> List[str]:
    """Split SQL content into meaningful chunks."""
    lines = content.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        current_chunk.append(line)
        current_size += len(line)
        
        # End chunk on semicolon or when size limit reached
        if line.endswith(';') or current_size >= chunk_size:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
    
    # Add remaining content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def main():
    """Run comparison analysis."""
    logger.info("Starting enhanced vs original semantic matching comparison...")
    
    # Read test files
    sql_files = read_test_sql_files()
    logger.info(f"Found {len(sql_files)} SQL test files")
    
    if not sql_files:
        logger.error("No SQL files found. Please check that test_files directory exists and contains .sql files")
        return
    
    results = {
        'comparison_summary': {},
        'file_analyses': {}
    }
    
    total_orig_matches = 0
    total_enh_matches = 0
    total_chunks = 0
    
    for filename, content in sql_files.items():
        logger.info(f"\nAnalyzing {filename}...")
        
        chunks = chunk_sql_content(content)
        file_results = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 20:  # Skip very small chunks
                continue
                
            total_chunks += 1
            analysis = analyze_code_chunk(
                chunk, filename, 
                find_relevant_rules, 
                find_relevant_rules_enhanced
            )
            
            total_orig_matches += analysis['original']['total_matches']
            total_enh_matches += analysis['enhanced']['total_matches']
            
            file_results.append(analysis)
            
            # Print summary for each chunk
            print(f"  Chunk {i+1}: Original={analysis['original']['total_matches']}, Enhanced={analysis['enhanced']['total_matches']}")
            
            # Show enhanced match details if available
            enh_rules = analysis['enhanced']['rules']
            if enh_rules['good_practices'] or enh_rules['bad_practices']:
                print(f"    Enhanced matches:")
                for rule in enh_rules['good_practices'] + enh_rules['bad_practices']:
                    match_info = f"confidence={rule.get('confidence', 'N/A'):.3f}" if 'confidence' in rule else f"score={rule.get('match_score', 'N/A')}"
                    match_type = rule.get('match_type', 'unknown')
                    print(f"      - {rule['title']} ({match_type}, {match_info})")
                    
                    # Show all similarities for enhanced matches
                    if 'all_similarities' in rule:
                        sim_details = ", ".join([f"{k}={v:.3f}" for k, v in rule['all_similarities'].items()])
                        print(f"        Similarities: {sim_details}")
        
        results['file_analyses'][filename] = file_results
        
        # File summary
        file_orig_total = sum(r['original']['total_matches'] for r in file_results)
        file_enh_total = sum(r['enhanced']['total_matches'] for r in file_results)
        print(f"  File totals: Original={file_orig_total}, Enhanced={file_enh_total}")
    
    # Overall summary
    results['comparison_summary'] = {
        'total_chunks_analyzed': total_chunks,
        'original_total_matches': total_orig_matches,
        'enhanced_total_matches': total_enh_matches,
        'improvement_ratio': total_enh_matches / total_orig_matches if total_orig_matches > 0 else float('inf'),
        'average_matches_per_chunk': {
            'original': total_orig_matches / total_chunks if total_chunks > 0 else 0,
            'enhanced': total_enh_matches / total_chunks if total_chunks > 0 else 0
        }
    }
    
    logger.info(f"\n=== COMPARISON SUMMARY ===")
    logger.info(f"Total chunks analyzed: {total_chunks}")
    logger.info(f"Original method total matches: {total_orig_matches}")
    logger.info(f"Enhanced method total matches: {total_enh_matches}")
    if total_orig_matches > 0:
        logger.info(f"Improvement ratio: {results['comparison_summary']['improvement_ratio']:.2f}x")
    else:
        logger.info(f"Improvement: Enhanced found {total_enh_matches} matches vs 0 from original")
    logger.info(f"Average matches per chunk - Original: {results['comparison_summary']['average_matches_per_chunk']['original']:.2f}")
    logger.info(f"Average matches per chunk - Enhanced: {results['comparison_summary']['average_matches_per_chunk']['enhanced']:.2f}")
    
    # Save detailed results - use relative path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(script_dir, "outputs")
    
    # Create outputs directory if it doesn't exist
    os.makedirs(outputs_dir, exist_ok=True)
    
    output_file = os.path.join(outputs_dir, "enhanced_vs_original_comparison.json")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Detailed results saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save results: {e}")

if __name__ == "__main__":
    main()