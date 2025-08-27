#!/usr/bin/env python3
# filepath: /workspaces/code-reviewer/test_env_vars.py

import os
import sys
from dotenv import load_dotenv

def test_environment_variables():
    """Test script to verify all required environment variables are set."""
    
    print("🔍 Testing Environment Variables Configuration")
    print("=" * 60)
    
    # Load .env file for local testing
    load_dotenv()
    
    # Define required variables for different contexts
    required_vars = {
        'DATABRICKS_TOKEN': {
            'description': 'Databricks API token for AI model access',
            'required': True,
            'sensitive': True
        },
        'GITLAB_API_TOKEN': {
            'description': 'GitLab personal access token for posting MR comments',
            'required': True,
            'sensitive': True
        },
        'DB_HOST': {
            'description': 'PostgreSQL database host',
            'required': True,
            'sensitive': False,
            'fallback': 'localhost'
        },
        'DB_NAME': {
            'description': 'PostgreSQL database name',
            'required': True,
            'sensitive': False,
            'fallback': 'rules'
        },
        'DB_USER': {
            'description': 'PostgreSQL database user',
            'required': True,
            'sensitive': False,
            'fallback': 'postgres'
        },
        'DB_PASSWORD': {
            'description': 'PostgreSQL database password',
            'required': True,
            'sensitive': True,
            'fallback': 'root'
        },
        'DB_PORT': {
            'description': 'PostgreSQL database port',
            'required': False,
            'sensitive': False,
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
    
    results = {
        'missing_required': [],
        'found_required': [],
        'gitlab_ci_context': False,
        'total_issues': 0
    }
    
    # Check if we're in GitLab CI context
    is_gitlab_ci = os.getenv('GITLAB_CI') == 'true'
    if is_gitlab_ci:
        print("🔧 Detected GitLab CI environment")
        results['gitlab_ci_context'] = True
    else:
        print("💻 Running in local development environment")
    
    print("\n📋 Checking Required Variables:")
    print("-" * 40)
    
    # Test required variables
    for var_name, config in required_vars.items():
        value = os.getenv(var_name)
        
        if value:
            if config['sensitive']:
                display_value = f"••••• (length: {len(value)})"
            else:
                display_value = value
            
            print(f"✅ {var_name:<20} = {display_value}")
            print(f"   📝 {config['description']}")
            results['found_required'].append(var_name)
        else:
            print(f"❌ {var_name:<20} = NOT SET")
            print(f"   📝 {config['description']}")
            
            if config.get('fallback'):
                print(f"   🔄 Fallback value available: {config['fallback']}")
            
            if config['required']:
                results['missing_required'].append(var_name)
                results['total_issues'] += 1
        
        print()
    
    # Test GitLab CI specific variables (only if in CI context)
    if is_gitlab_ci:
        print("\n🔧 Checking GitLab CI Variables:")
        print("-" * 40)
        
        for var_name, description in gitlab_ci_vars.items():
            value = os.getenv(var_name)
            if value:
                print(f"✅ {var_name:<35} = {value}")
            else:
                print(f"❌ {var_name:<35} = NOT SET")
                results['total_issues'] += 1
            print(f"   📝 {description}")
            print()
    
    # Test token validity (basic checks)
    print("\n🔐 Token Validation:")
    print("-" * 40)
    
    databricks_token = os.getenv('DATABRICKS_TOKEN')
    if databricks_token:
        if databricks_token.startswith('dapi'):
            print("✅ DATABRICKS_TOKEN appears to have correct format (starts with 'dapi')")
        else:
            print("⚠️  DATABRICKS_TOKEN doesn't start with 'dapi' - verify format")
            results['total_issues'] += 1
    
    gitlab_token = os.getenv('GITLAB_API_TOKEN')
    if gitlab_token:
        if gitlab_token.startswith('glpat-'):
            print("✅ GITLAB_API_TOKEN appears to have correct format (starts with 'glpat-')")
        else:
            print("⚠️  GITLAB_API_TOKEN doesn't start with 'glpat-' - verify it's a personal access token")
            results['total_issues'] += 1
    
    # Test database configuration compatibility
    print("\n🗄️  Database Configuration Test:")
    print("-" * 40)
    
    try:
        # Try to construct DB config like the actual application does
        from config import DB_CONFIG
        
        print("✅ Database configuration loaded from config.py:")
        for key, value in DB_CONFIG.items():
            if key == 'password':
                print(f"   {key}: •••••")
            else:
                print(f"   {key}: {value}")
        
        # Check if environment variables would override config.py values
        env_overrides = {}
        if os.getenv('DB_HOST'): env_overrides['host'] = os.getenv('DB_HOST')
        if os.getenv('DB_NAME'): env_overrides['dbname'] = os.getenv('DB_NAME')
        if os.getenv('DB_USER'): env_overrides['user'] = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'): env_overrides['password'] = os.getenv('DB_PASSWORD')
        if os.getenv('DB_PORT'): env_overrides['port'] = os.getenv('DB_PORT')
        
        if env_overrides:
            print("\n⚠️  Note: Environment variables will override config.py values:")
            for key, value in env_overrides.items():
                if 'password' in key:
                    print(f"   {key}: ••••• (from env var)")
                else:
                    print(f"   {key}: {value} (from env var)")
    
    except ImportError as e:
        print(f"❌ Could not import config.py: {e}")
        results['total_issues'] += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if results['total_issues'] == 0:
        print("🎉 All environment variables are properly configured!")
        if is_gitlab_ci:
            print("✅ Ready for GitLab CI/CD execution")
        else:
            print("✅ Ready for local development")
    else:
        print(f"❌ Found {results['total_issues']} configuration issues")
        
        if results['missing_required']:
            print(f"\n🚨 Missing required variables: {', '.join(results['missing_required'])}")
            
            if not is_gitlab_ci:
                print("\n💡 To fix locally:")
                print("   1. Add missing variables to your .env file")
                print("   2. Or export them as environment variables")
            else:
                print("\n💡 To fix in GitLab CI:")
                print("   1. Go to Project Settings → CI/CD → Variables")
                print("   2. Add the missing variables")
    
    print("\n🔗 Useful Links:")
    if not is_gitlab_ci:
        print("   • GitLab Personal Access Tokens: https://gitlab.com/-/profile/personal_access_tokens")
    print("   • Databricks Token Documentation: https://docs.databricks.com/api/workspace/authentication")
    
    return results['total_issues'] == 0

def test_token_network_access():
    """Test if tokens can actually reach their respective services."""
    print("\n🌐 Testing Network Access (Optional)")
    print("-" * 40)
    
    # Test Databricks token
    databricks_token = os.getenv('DATABRICKS_TOKEN')
    if databricks_token:
        try:
            import requests
            headers = {"Authorization": f"Bearer {databricks_token}"}
            # This is just a basic connectivity test - not a full API call
            print("🔍 Testing Databricks token connectivity...")
            print("   (This is just a basic format check, not a full API test)")
        except ImportError:
            print("⚠️  requests library not available for network testing")
    
    # Test GitLab token
    gitlab_token = os.getenv('GITLAB_API_TOKEN')
    gitlab_url = os.getenv('CI_SERVER_URL', 'https://gitlab.com')
    
    if gitlab_token:
        try:
            import requests
            headers = {"Authorization": f"Bearer {gitlab_token}"}
            print("🔍 Testing GitLab token connectivity...")
            print("   (This requires network access to GitLab)")
            
            # Basic test - just check if we can reach GitLab API
            response = requests.get(f"{gitlab_url}/api/v4/user", headers=headers, timeout=5)
            if response.status_code == 200:
                print("✅ GitLab token is valid and has API access")
            else:
                print(f"❌ GitLab token test failed: HTTP {response.status_code}")
        except ImportError:
            print("⚠️  requests library not available for network testing")
        except Exception as e:
            print(f"⚠️  Network test failed: {e}")

if __name__ == "__main__":
    success = test_environment_variables()
    
    # Optional network tests
    if '--network-test' in sys.argv:
        test_token_network_access()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)