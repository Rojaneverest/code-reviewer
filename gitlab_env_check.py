#!/usr/bin/env python3
"""
GitLab CI/CD Environment Validation Script
Validates that all required environment variables are available for the AI code reviewer
"""

import os
import sys

def check_environment_variables():
    """Check if all required environment variables are set."""
    print("GitLab CI/CD Environment Validation")
    print("=" * 50)
    
    required_vars = {
        'CI_PROJECT_ID': 'GitLab project ID',
        'CI_MERGE_REQUEST_IID': 'Merge request internal ID',
        'GITLAB_API_TOKEN': 'GitLab API token for posting comments',
        'DATABRICKS_TOKEN': 'Databricks token for LLM access'
    }
    
    database_vars = {
        'DB_HOST': 'Database host',
        'DB_PORT': 'Database port', 
        'DB_NAME': 'Database name',
        'DB_USER': 'Database user',
        'DB_PASSWORD': 'Database password'
    }
    
    print("\nChecking Required GitLab CI Variables:")
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if 'token' in var.lower():
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  OK: {var} = {display_value}")
        else:
            print(f"  MISSING: {var} ({description})")
            missing_vars.append(var)
    
    print("\nChecking Database Configuration:")
    db_missing = []
    for var, description in database_vars.items():
        value = os.getenv(var)
        if value:
            if 'password' in var.lower():
                display_value = "***"
            else:
                display_value = value
            print(f"  OK: {var} = {display_value}")
        else:
            print(f"  MISSING: {var} ({description})")
            db_missing.append(var)
    
    print("\n" + "=" * 50)
    
    if missing_vars:
        print(f"ERROR: Missing required GitLab CI variables: {', '.join(missing_vars)}")
        print("Please set these in your GitLab project CI/CD settings.")
        return False
    
    if db_missing:
        print(f"WARNING: Missing database variables: {', '.join(db_missing)}")
        print("Database connectivity will not be available.")
        print("AI review will continue with limited functionality.")
    
    print("SUCCESS: All required environment variables are available!")
    return True

def main():
    """Main execution function."""
    try:
        success = check_environment_variables()
        if success:
            print("\nEnvironment validation completed successfully.")
            sys.exit(0)
        else:
            print("\nEnvironment validation failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\nError during environment validation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()