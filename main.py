import argparse
import os
import json
import re
from rag.retriever import find_relevant_rules
from rag.generator import generate_review
from utils.line_mapper import map_sql_statements_to_lines
from utils.chunker import chunk_pyspark_file

def analyze_code(file_path):
    """Analyzes a code file using the RAG model, processing it in chunks."""
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    # Determine language from file extension
    _, file_extension = os.path.splitext(file_path)
    language = ""
    if file_extension == '.sql':
        language = 'SQL'
        chunks = map_sql_statements_to_lines(file_content)
    elif file_extension == '.py':
        language = 'PySpark' # Assuming .py is PySpark for this project
        chunks = chunk_pyspark_file(file_content)
    else:
        print(f"Unsupported file type: {file_extension}")
        return

    all_issues = []

    print(f"Analyzing {file_path} (Language: {language}), found {len(chunks)} chunks...")

    for code_chunk, start_line in chunks:
        # Strip the chunk of any leading/trailing whitespace that might confuse the LLM
        code_chunk = code_chunk.strip()
        if not code_chunk:
            continue

        # Find relevant rules for the current chunk using the hybrid retriever
        relevant_rules, log_method = find_relevant_rules(code_chunk, language=language)

        print(f"\nProcessing chunk (lines {start_line}-{start_line + code_chunk.count('\n')}) with: {log_method}")

        # Generate a review for the chunk
        review = generate_review(code_chunk, relevant_rules, log_method)
        if review and review.get('issues_found', 0) > 0:
            # Adjust line numbers to be relative to the entire file
            for issue in review['issues']:
                # The 'start_line' from the chunk is the correct, absolute line number.
                # The LLM might return a relative line number, but for single-line chunks, it's always 1.
                # So, we can just use the start_line.
                issue['line_number'] = start_line
            all_issues.extend(review['issues'])

    # 3. Assemble the final JSON report
    final_report = {
        "file_name": os.path.basename(file_path),
        "issues_found": len(all_issues),
        "issues": all_issues
    }

    # 4. Print the final JSON report
    print("\n--- Code Review Report ---")
    print(json.dumps(final_report, indent=4))
    print("--- End of Report ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI Code Review Agent')
    parser.add_argument('file_path', type=str, help='The path to the code file to be reviewed.')
    args = parser.parse_args()
    
    analyze_code(args.file_path)
