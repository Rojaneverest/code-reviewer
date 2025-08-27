#!/usr/bin/env python3
# filepath: /workspaces/code-reviewer/gitlab_env_check.py

import os
import sys

def check_gitlab_ci_variables():
    """Check GitLab CI/CD environment variables specifically."""
    
    print("🔍 GitLab CI/CD Environment Variables Check")
    print("=" * 60)
    
    # Check if we're actually in GitLab CI
    is_gitlab_ci = os.getenv('GITLAB_CI') == 'true'
    
    if not is_gitlab_ci:
        print("⚠️  Not running in GitLab CI environment")
        print("   GITLAB_CI environment variable is not set to 'true'")
        return False
    
    print("✅ Confirmed: Running in GitLab CI environment")
    
    # Required variables for SQL code review
    required_vars = {
        'DATABRICKS_TOKEN': {
            'description': 'Databricks API token for AI model access',
            'expected_prefix': 'dapi'
        },
        'GITLAB_API_TOKEN': {
            'description': 'GitLab personal access token for posting MR comments',
            'expected_prefix': 'glpat-'
        },
        'host': {
            'description': 'PostgreSQL database host (should be "postgres" in GitLab CI)',
            'fallback': 'postgres'
        },
        'dbname': {
            'description': 'PostgreSQL database name',
            'fallback': 'rules'
        },
        'user': {
            'description': 'PostgreSQL database user',
            'fallback': 'postgres'
        },
        'password': {
            'description': 'PostgreSQL database password',
            'fallback': None
        },
        'port': {
            'description': 'PostgreSQL database port',
            'fallback': '5432'
        }
    }
    
    # GitLab CI specific variables
    gitlab_ci_vars = {
        'CI_PROJECT_ID': 'GitLab project ID',
        'CI_MERGE_REQUEST_IID': 'Merge request internal ID',
        'CI_MERGE_REQUEST_TARGET_BRANCH_NAME': 'Target branch name',
        'CI_MERGE_REQUEST_SOURCE_BRANCH_NAME': 'Source branch name',
        'CI_SERVER_URL': 'GitLab server URL',
        'CI_PIPELINE_SOURCE': 'Pipeline source (should be "merge_request_event")'
    }
    
    missing_vars = []
    invalid_tokens = []
    
    print("\n📋 Checking Required Application Variables:")
    print("-" * 50)
    
    for var_name, config in required_vars.items():
        value = os.getenv(var_name)
        
        if value:
            # Mask sensitive values for display
            if 'TOKEN' in var_name or 'PASSWORD' in var_name:
                display_value = f"••••• (length: {len(value)})"
            else:
                display_value = value
            
            print(f"✅ {var_name:<20} = {display_value}")
            
            # Check token format if specified
            if 'expected_prefix' in config:
                if not value.startswith(config['expected_prefix']):
                    print(f"   ⚠️  Warning: Expected to start with '{config['expected_prefix']}'")
                    invalid_tokens.append(var_name)
        else:
            print(f"❌ {var_name:<20} = NOT SET")
            if config.get('fallback'):
                print(f"   💡 Fallback available: {config['fallback']}")
            else:
                missing_vars.append(var_name)
        
        print(f"   📝 {config['description']}")
        print()
    
    print("\n🔧 Checking GitLab CI Variables:")
    print("-" * 50)
    
    gitlab_missing = []
    for var_name, description in gitlab_ci_vars.items():
        value = os.getenv(var_name)
        
        if value:
            print(f"✅ {var_name:<35} = {value}")
        else:
            print(f"❌ {var_name:<35} = NOT SET")
            gitlab_missing.append(var_name)
        
        print(f"   📝 {description}")
        print()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    total_issues = len(missing_vars) + len(invalid_tokens) + len(gitlab_missing)
    
    if total_issues == 0:
        print("🎉 All environment variables are properly configured!")
        print("✅ Ready for SQL code review execution")
        return True
    else:
        print(f"❌ Found {total_issues} configuration issues:")
        
        if missing_vars:
            print(f"\n🚨 Missing required variables: {', '.join(missing_vars)}")
            print("   💡 Add these in GitLab Project Settings → CI/CD → Variables")
        
        if invalid_tokens:
            print(f"\n⚠️  Invalid token formats: {', '.join(invalid_tokens)}")
            print("   💡 Verify token formats in GitLab CI/CD Variables")
        
        if gitlab_missing:
            print(f"\n🔧 Missing GitLab CI variables: {', '.join(gitlab_missing)}")
            print("   💡 These should be automatically provided by GitLab")
            print("   💡 Check if this job is running in the correct context")
        
        print("\n🔗 Troubleshooting:")
        print("   • GitLab CI/CD Variables: Settings → CI/CD → Variables")
        print("   • Personal Access Tokens: Profile → Access Tokens")
        print("   • Databricks Tokens: Databricks Console → User Settings")
        
        return False

def test_pipeline_context():
    """Test if we're in the correct pipeline context."""
    print("\n🎯 Pipeline Context Check:")
    print("-" * 30)
    
    pipeline_source = os.getenv('CI_PIPELINE_SOURCE')
    expected_source = 'merge_request_event'
    
    if pipeline_source == expected_source:
        print(f"✅ Correct pipeline source: {pipeline_source}")
        return True
    else:
        print(f"⚠️  Pipeline source: {pipeline_source}")
        print(f"   Expected: {expected_source}")
        print("   This job is configured to run only on merge requests")
        return False

if __name__ == "__main__":
    print("🚀 GitLab CI/CD Environment Validation")
    print("=" * 60)
    
    # Check if we're in GitLab CI
    if not os.getenv('GITLAB_CI'):
        print("❌ This script is designed to run in GitLab CI/CD")
        print("   GITLAB_CI environment variable not found")
        print("\n💡 For local testing, use: python test_env_vars.py")
        sys.exit(1)
    
    # Check pipeline context
    context_ok = test_pipeline_context()
    
    # Check environment variables
    vars_ok = check_gitlab_ci_variables()
    
    # Exit with appropriate code
    if vars_ok and context_ok:
        print("\n🎉 All checks passed! Proceeding with SQL code review...")
        sys.exit(0)
    else:
        print("\n❌ Environment validation failed!")
        sys.exit(1)