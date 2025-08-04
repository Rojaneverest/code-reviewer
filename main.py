import argparse
import os
import json
from rag.retriever import retrieve_relevant_rules
from rag.generator import generate_review
from utils.chunker import chunk_code

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
    elif file_extension == '.py':
        language = 'PySpark' # Assuming .py is PySpark for this project
    else:
        print(f"Unsupported file type: {file_extension}")
        return

    # Get code chunks with their starting line numbers
    chunks = chunk_code(file_path, file_content)
    all_issues = []

    print(f"Analyzing {file_path} (Language: {language}), found {len(chunks)} chunks...")

    # 1. Retrieve all relevant rules for the language once
    rules = retrieve_relevant_rules(None, language) # Pass None for code_chunk as it's not used for rule retrieval anymore
    if not rules:
        print("No relevant rules found for this language.")
        return

    for code_chunk, start_line in chunks:
        # 2. Generate the review for each chunk
        review_result = generate_review(code_chunk, rules)

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
