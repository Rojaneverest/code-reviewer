import argparse
import os
import json
from rag.retriever import get_all_rules_for_language, find_relevant_rules
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

    # 1. Retrieve all rules for the language once.
    all_rules = get_all_rules_for_language(language)
    if not all_rules:
        print("Could not retrieve any rules for this language.")
        return

    for code_chunk, start_line in chunks:
        # 2. Find the subset of relevant rules for the current chunk.
        relevant_rules = find_relevant_rules(code_chunk, all_rules)
        
        # 3. Generate the review for the chunk with only the relevant rules.
        review_result = generate_review(code_chunk, relevant_rules)

        if review_result and review_result.get('issues'):
            for issue in review_result['issues']:
                # Adjust line number to be absolute within the file
                original_line = issue.get('line_number')
                if isinstance(original_line, int):
                    issue['line_number'] = original_line + start_line - 1
                else:
                    # If the model didn't provide a valid line number, default to the start of the chunk.
                    issue['line_number'] = start_line
                all_issues.append(issue)

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
