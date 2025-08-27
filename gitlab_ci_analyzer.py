import os
import subprocess
import re
import json
import sqlparse
from utils.line_mapper import map_sql_statements_to_lines
from rag.retriever import find_relevant_rules
from rag.generator import generate_review
from utils.line_mapper import map_sql_statements_to_lines

def get_changed_files(target_branch, source_branch):
    """Get a list of changed .sql files between two branches."""
    try:
        # Ensure the target branch is available for comparison
        subprocess.run(['git', 'fetch', 'origin', target_branch], check=True, capture_output=True, text=True)
        
        # Get the diff
        diff_process = subprocess.run(
            ['git', 'diff', f"origin/{target_branch}...{source_branch}", '--name-only'],
            check=True,
            capture_output=True,
            text=True
        )
        files = diff_process.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.sql') and os.path.exists(f)]
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e.stderr}")
        return []

def get_changed_lines(file_path, target_branch, source_branch):
    """Get the line numbers of added/modified lines in the source branch version of the file."""
    changed_lines = set()
    try:
        diff_process = subprocess.run(
            ['git', 'diff', f"origin/{target_branch}...{source_branch}", '--', file_path],
            check=True,
            capture_output=True,
            text=True
        )
        diff_output = diff_process.stdout
        
        # Regex to find hunk headers, e.g., @@ -1,5 +1,6 @@
        hunk_header_re = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@')
        
        current_line_in_new_file = 0
        for line in diff_output.split('\n'):
            match = hunk_header_re.match(line)
            if match:
                current_line_in_new_file = int(match.group(1))
                continue
            
            if line.startswith('+') and not line.startswith('+++'):
                changed_lines.add(current_line_in_new_file)
                current_line_in_new_file += 1
            elif not line.startswith('-'):
                current_line_in_new_file += 1
                
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed lines for {file_path}: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred while processing diff for {file_path}: {e}")
        
    return changed_lines

def map_lines_to_statements(file_path):
    """Map each line number in the file to the SQL statement it belongs to."""
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        # Use our existing line mapper to get statements and their start lines
        statements_with_lines = map_sql_statements_to_lines(file_content)
        
        # Create a mapping from line numbers to statements
        line_to_statement = {}
        
        for statement, start_line in statements_with_lines:
            statement_lines = statement.split('\n')
            for i, line in enumerate(statement_lines):
                line_number = start_line + i
                line_to_statement[line_number] = {
                    'statement': statement,
                    'start_line': start_line
                }
        
        return line_to_statement
        
    except Exception as e:
        print(f"Error mapping lines to statements for {file_path}: {e}")
        return {}

def get_changed_statements(file_path, changed_lines):
    """Get the unique SQL statements that contain the changed lines."""
    line_to_statement = map_lines_to_statements(file_path)
    changed_statements = {}
    
    for line_num in changed_lines:
        if line_num in line_to_statement:
            stmt_info = line_to_statement[line_num]
            statement = stmt_info['statement']
            start_line = stmt_info['start_line']
            
            # Use the statement as key to ensure uniqueness
            changed_statements[statement] = {
                'statement': statement,
                'start_line': start_line,
                'file_path': file_path
            }
    
    return list(changed_statements.values())

def analyze_statement(statement_info):
    """Analyze a single SQL statement using our existing RAG system."""
    statement = statement_info['statement']
    start_line = statement_info['start_line']
    file_path = statement_info['file_path']
    
    print(f"  Analyzing statement starting at line {start_line}...")
    
    # Find relevant rules for the statement
    relevant_rules, log_method = find_relevant_rules(statement, language='SQL')
    
    # Generate review using our existing system
    review = generate_review(statement, relevant_rules, log_method)
    
    if review and review.get('issues_found', 0) > 0:
        # Adjust line numbers to be relative to the entire file
        for issue in review['issues']:
            relative_line = issue.get('line_number', 1)
            issue['line_number'] = start_line + relative_line - 1
            issue['file_path'] = file_path
        
        return review['issues']
    
    return []

def main(target_branch, source_branch):
    """Main function to analyze changed SQL files."""
    changed_files = get_changed_files(target_branch, source_branch)
    
    if not changed_files:
        print("No changed .sql files found.")
        return

    print(f"Found changed SQL files: {changed_files}")

    all_issues = []

    for file_path in changed_files:
        print(f"\nAnalyzing file: {file_path}")
        
        # Get the lines that were changed in this file
        changed_lines = get_changed_lines(file_path, target_branch, source_branch)
        
        if not changed_lines:
            print(f"  No changed lines found in {file_path}")
            continue
            
        print(f"  Changed lines: {sorted(changed_lines)}")
        
        # Get the complete SQL statements that contain the changed lines
        changed_statements = get_changed_statements(file_path, changed_lines)
        
        if not changed_statements:
            print(f"  No SQL statements found for changed lines in {file_path}")
            continue
            
        print(f"  Found {len(changed_statements)} statements to analyze")
        
        # Analyze each changed statement
        for statement_info in changed_statements:
            issues = analyze_statement(statement_info)
            all_issues.extend(issues)

    # Format results for GitLab comment
    if all_issues:
        print(f"\n--- Analysis Complete: Found {len(all_issues)} total issues ---")
        format_issues_for_gitlab(all_issues)
    else:
        print("\n--- Analysis Complete: No issues found ---")

def format_issues_for_gitlab(issues):
    """Format the issues as a GitLab-friendly markdown comment."""
    comment = "## 🔍 SQL Code Review Results\n\n"
    
    if not issues:
        comment += "✅ No issues found in the changed SQL code.\n"
        return comment
    
    comment += f"Found **{len(issues)}** issue(s) in the changed SQL code:\n\n"
    
    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        file_path = issue.get('file_path', 'Unknown')
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)
    
    for file_path, file_issues in issues_by_file.items():
        comment += f"### 📄 `{file_path}`\n\n"
        
        for issue in file_issues:
            severity = issue.get('severity', 'Unknown')
            line_num = issue.get('line_number', 'Unknown')
            suggestion = issue.get('suggestion', 'No suggestion provided')
            rule_id = issue.get('rule_id', '')
            
            # Choose emoji based on severity
            if severity == 'Critical':
                emoji = '🔴'
            elif severity == 'Major':
                emoji = '🟠'
            elif severity == 'Minor':
                emoji = '🟡'
            else:
                emoji = '💡'
            
            comment += f"{emoji} **Line {line_num}** - {severity}"
            if rule_id:
                comment += f" (Rule {rule_id})"
            comment += f"\n> {suggestion}\n\n"
    
    comment += "---\n*This comment was generated automatically by the SQL Code Review bot.*"
    
    print("\n--- GitLab Comment ---")
    print(comment)
    print("--- End Comment ---")
    
    return comment


if __name__ == '__main__':
    # These would be provided by the GitLab CI/CD environment
    # Example: CI_MERGE_REQUEST_TARGET_BRANCH_NAME and CI_COMMIT_BRANCH
    target = os.environ.get("CI_MERGE_REQUEST_TARGET_BRANCH_NAME", "main")
    source = os.environ.get("CI_COMMIT_BRANCH", "v1-CICD-CR")
    
    main(target, source)
