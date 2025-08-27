#!/usr/bin/env python3

import subprocess
import os
import sys
import json
import requests
from typing import List, Dict, Tuple
import sqlparse

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_gitlab_env_vars():
    """Get required GitLab CI environment variables."""
    required_vars = {
        'CI_PROJECT_ID': os.environ.get('CI_PROJECT_ID'),
        'CI_MERGE_REQUEST_IID': os.environ.get('CI_MERGE_REQUEST_IID'),
        'CI_MERGE_REQUEST_TARGET_BRANCH_NAME': os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_NAME', 'main'),
        'CI_MERGE_REQUEST_SOURCE_BRANCH_NAME': os.environ.get('CI_MERGE_REQUEST_SOURCE_BRANCH_NAME'),
        'GITLAB_API_TOKEN': os.environ.get('GITLAB_API_TOKEN'),
        'CI_SERVER_URL': os.environ.get('CI_SERVER_URL', 'https://gitlab.com')
    }
    
    missing_vars = [k for k, v in required_vars.items() if v is None]
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        return None
    
    return required_vars

def get_changed_files(target_branch: str, source_branch: str) -> List[str]:
    """Get list of changed .sql files between two branches."""
    try:
        # First, fetch all remotes to ensure we have the latest refs
        print(f"Fetching remote branches...")
        subprocess.run(['git', 'fetch', 'origin'], check=True, capture_output=True)
        
        # Try different git diff strategies
        diff_commands = [
            ['git', 'diff', '--name-only', f'origin/{target_branch}...HEAD'],
            ['git', 'diff', '--name-only', f'{target_branch}...HEAD'],
            ['git', 'diff', '--name-only', f'origin/{target_branch}', 'HEAD'],
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD']  # Fallback: compare with previous commit
        ]
        
        for i, cmd in enumerate(diff_commands):
            try:
                print(f"Trying git diff strategy {i+1}: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                all_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                sql_files = [f for f in all_files if f.endswith('.sql') and f.strip()]
                
                print(f"✅ Strategy {i+1} worked! Found {len(sql_files)} changed SQL files:")
                for file in sql_files:
                    print(f"  - {file}")
                
                return sql_files
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Strategy {i+1} failed: {e}")
                continue
        
        # If all strategies fail, return empty list
        print("⚠️  All git diff strategies failed. No files to analyze.")
        return []
        
    except Exception as e:
        print(f"Error in get_changed_files: {e}")
        return []

def get_changed_lines(file_path: str, target_branch: str, source_branch: str) -> List[int]:
    """Get line numbers that were added or modified in the source branch."""
    try:
        # Try different git diff strategies for line changes
        diff_commands = [
            ['git', 'diff', f'origin/{target_branch}...HEAD', '--', file_path],
            ['git', 'diff', f'{target_branch}...HEAD', '--', file_path],
            ['git', 'diff', f'origin/{target_branch}', 'HEAD', '--', file_path],
            ['git', 'diff', 'HEAD~1', 'HEAD', '--', file_path]  # Fallback
        ]
        
        for cmd in diff_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                break
            except subprocess.CalledProcessError:
                continue
        else:
            print(f"Warning: Could not get diff for {file_path}")
            return []
        
        changed_lines = []
        current_new_line = 0
        
        for line in result.stdout.split('\n'):
            if line.startswith('@@'):
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                parts = line.split()
                if len(parts) >= 3:
                    new_info = parts[2][1:]  # Remove the '+' prefix
                    current_new_line = int(new_info.split(',')[0])
            elif line.startswith('+') and not line.startswith('+++'):
                # This is an added line
                changed_lines.append(current_new_line)
                current_new_line += 1
            elif not line.startswith('-') and not line.startswith('\\'):
                # This is a context line (unchanged)
                current_new_line += 1
        
        print(f"Changed lines in {file_path}: {changed_lines}")
        return changed_lines
    
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed lines for {file_path}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while processing diff for {file_path}: {e}")
        return []

def map_lines_to_statements(file_content: str, changed_lines: List[int]) -> List[Tuple[str, int, int]]:
    """Map changed lines to complete SQL statements."""
    if not changed_lines:
        return []
    
    statements = sqlparse.split(file_content)
    statement_mappings = []
    current_line = 1
    
    for statement in statements:
        if statement.strip():
            statement_lines = statement.count('\n') + 1
            start_line = current_line
            end_line = current_line + statement_lines - 1
            
            # Check if any changed line falls within this statement
            if any(start_line <= line <= end_line for line in changed_lines):
                statement_mappings.append((statement.strip(), start_line, end_line))
                print(f"Found changed statement (lines {start_line}-{end_line})")
            
            current_line = end_line + 1
    
    return statement_mappings

def analyze_sql_statements(statements_to_review: List[Tuple[str, int, int]]) -> Dict:
    """Analyze SQL statements and return review results."""
    print(f"\n=== Analyzing {len(statements_to_review)} SQL statements ===")
    
    all_issues = []
    
    for statement, start_line, end_line in statements_to_review:
        print(f"\nAnalyzing statement at lines {start_line}-{end_line}")
        
        try:
            # Import and use our existing analysis logic
            from main import analyze_code_chunk
            
            # Analyze this specific statement
            issues = analyze_code_chunk(statement, language='SQL')
            
            # Add line number context and adjust line numbers
            for issue in issues:
                # Adjust the line number to be relative to the file, not the chunk
                original_line = issue.get('line_number', 1)
                adjusted_line = start_line + original_line - 1
                issue['line_number'] = adjusted_line
                issue['file_line_range'] = f"{start_line}-{end_line}"
                all_issues.append(issue)
                
        except Exception as e:
            print(f"Error analyzing statement: {e}")
            # Create a fallback issue
            all_issues.append({
                'line_number': start_line,
                'severity': 'Error',
                'suggestion': f'Failed to analyze this SQL statement: {str(e)}',
                'file_line_range': f"{start_line}-{end_line}"
            })
    
    return {
        'total_issues': len(all_issues),
        'issues': all_issues
    }

def format_gitlab_comment(results: Dict, changed_files: List[str]) -> str:
    """Format results as a GitLab merge request comment."""
    if results['total_issues'] == 0:
        return """## 🎉 SQL Code Review - No Issues Found!

Your SQL changes look good! No code quality issues were detected.

*Automated review by SQL Code Reviewer*"""
    
    comment = f"""## 🔍 SQL Code Review Results

Found **{results['total_issues']} issues** in {len(changed_files)} changed SQL file(s):

"""
    
    # Group issues by file
    issues_by_file = {}
    for issue in results['issues']:
        file_name = "Unknown file"  # We'll enhance this later to track file names
        if file_name not in issues_by_file:
            issues_by_file[file_name] = []
        issues_by_file[file_name].append(issue)
    
    # Format issues
    for i, issue in enumerate(results['issues'], 1):
        severity_emoji = {
            'Critical': '🚨',
            'Major': '⚠️',
            'Minor': '💡',
            'AI Generated Suggestion': '🤖'
        }.get(issue.get('severity', 'Unknown'), '❓')
        
        comment += f"""### {severity_emoji} Issue #{i} - {issue.get('severity', 'Unknown')}

**Line {issue.get('line_number', 'Unknown')}** ({issue.get('file_line_range', 'Unknown range')})

{issue.get('suggestion', 'No suggestion provided')}

---

"""
    
    comment += "\n*🤖 Automated review by SQL Code Reviewer*"
    return comment

def post_review_to_gitlab(comment: str, env_vars: Dict) -> bool:
    """Post the review comment to GitLab merge request."""
    url = f"{env_vars['CI_SERVER_URL']}/api/v4/projects/{env_vars['CI_PROJECT_ID']}/merge_requests/{env_vars['CI_MERGE_REQUEST_IID']}/notes"
    
    headers = {
        'Authorization': f"Bearer {env_vars['GITLAB_API_TOKEN']}",
        'Content-Type': 'application/json'
    }
    
    data = {
        'body': comment
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print("✅ Successfully posted review comment to GitLab MR")
            return True
        else:
            print(f"❌ Failed to post comment. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error posting to GitLab: {e}")
        return False

def main():
    """Main function for GitLab CI execution."""
    print("🚀 Starting SQL Code Review for GitLab MR")
    print("=" * 60)
    
    # Get GitLab environment variables
    env_vars = get_gitlab_env_vars()
    if not env_vars:
        print("❌ Missing required GitLab CI environment variables")
        sys.exit(1)
    
    target_branch = env_vars['CI_MERGE_REQUEST_TARGET_BRANCH_NAME']
    source_branch = env_vars['CI_MERGE_REQUEST_SOURCE_BRANCH_NAME']
    
    print(f"🔍 Analyzing changes from {source_branch} → {target_branch}")
    print(f"📋 Merge Request IID: {env_vars['CI_MERGE_REQUEST_IID']}")
    
    # Debug: Show git status
    print("\n🔧 Git Debug Information:")
    try:
        # Show current branch and commit
        current_branch = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, check=True)
        print(f"Current branch: {current_branch.stdout.strip()}")
        
        current_commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        print(f"Current commit: {current_commit.stdout.strip()}")
        
        # Show available branches
        branches = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True, check=True)
        print(f"Available branches:\n{branches.stdout}")
        
        # Show remotes
        remotes = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, check=True)
        print(f"Git remotes:\n{remotes.stdout}")
        
    except subprocess.CalledProcessError as e:
        print(f"Git debug failed: {e}")
    
    # Get changed SQL files
    changed_files = get_changed_files(target_branch, source_branch)
    
    if not changed_files:
        comment = """## 🔍 SQL Code Review

No SQL files were changed in this merge request.

*🤖 Automated review by SQL Code Reviewer*"""
        
        post_review_to_gitlab(comment, env_vars)
        print("✅ No SQL files to review")
        return
    
    all_results = {'total_issues': 0, 'issues': []}
    
    # Process each changed file
    for file_path in changed_files:
        print(f"\n📄 Processing file: {file_path}")
        print("-" * 40)
        
        # Get changed lines
        changed_lines = get_changed_lines(file_path, target_branch, source_branch)
        
        if not changed_lines:
            print(f"No line changes detected in {file_path}")
            continue
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
        
        # Map to statements
        statements_to_review = map_lines_to_statements(file_content, changed_lines)
        
        if not statements_to_review:
            print(f"No complete SQL statements found for changed lines in {file_path}")
            continue
        
        # Analyze statements
        file_results = analyze_sql_statements(statements_to_review)
        
        # Accumulate results
        all_results['total_issues'] += file_results['total_issues']
        all_results['issues'].extend(file_results['issues'])
    
    # Format and post results
    print("\n" + "=" * 60)
    print("📋 POSTING RESULTS TO GITLAB MR")
    print("=" * 60)
    
    comment = format_gitlab_comment(all_results, changed_files)
    success = post_review_to_gitlab(comment, env_vars)
    
    # Save results as artifacts
    with open('review_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📊 Summary: {all_results['total_issues']} issues found in {len(changed_files)} files")
    
    if success:
        print("✅ Review completed successfully!")
    else:
        print("⚠️  Review completed but failed to post comment")
        sys.exit(1)

if __name__ == "__main__":
    main()
