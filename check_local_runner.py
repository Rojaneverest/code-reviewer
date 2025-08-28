#!/usr/bin/env python3
"""
Local Runner Configuration Checker for AI Code Reviewer
This script validates that the local GitLab runner can access all required services.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check if all required environment variables are set."""
    print("🔍 Checking Environment Variables...")
    
    required_vars = {
        'Database Connection': [
            'host', 'port', 'dbname', 'user', 'password'
        ],
        'Databricks LLM': [
            'DATABRICKS_TOKEN', 'DATABRICKS_BASE_URL'
        ],
        'Databricks LLM (Optional)': [
            'DATABRICKS_ENDPOINT', 'DATABRICKS_MODEL_NAME', 'DATABRICKS_TIMEOUT'
        ],
        'GitLab Integration': [
            'GITLAB_API_TOKEN'
        ],
        'LM Studio (Optional Fallback)': [
            'ENABLE_LM_STUDIO_FALLBACK', 'LM_STUDIO_BASE_URL', 'LM_STUDIO_TIMEOUT'
        ]
    }
    
    all_good = True
    
    for category, vars_list in required_vars.items():
        print(f"\n  📋 {category}:")
        for var in vars_list:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if 'token' in var.lower() or 'password' in var.lower():
                    display_value = f"{'*' * (len(value) - 4)}{value[-4:]}" if len(value) > 4 else "****"
                else:
                    display_value = value
                print(f"    ✅ {var}: {display_value}")
            else:
                print(f"    ❌ {var}: Not set")
                all_good = False
    
    return all_good

def check_database_connection():
    """Test database connectivity."""
    print("\n🗄️  Testing Database Connection...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('host'),
            port=os.getenv('port'),
            database=os.getenv('dbname'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"    ✅ Database connection successful")
        print(f"    📋 PostgreSQL version: {version}")
        return True
        
    except Exception as e:
        print(f"    ❌ Database connection failed: {e}")
        return False

def check_databricks_llm():
    """Test Databricks LLM endpoint connectivity."""
    print("\n🤖 Testing Databricks LLM Connection...")
    
    # Import the configuration
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from config import LLM_CONFIG
    except ImportError as e:
        print(f"    ❌ Failed to import configuration: {e}")
        return False
    
    databricks_config = LLM_CONFIG["databricks"]
    
    if not databricks_config["enabled"]:
        print("    ❌ Databricks not enabled - token not configured")
        return False
    
    token = databricks_config["token"]
    base_url = databricks_config["base_url"]
    endpoint_path = databricks_config["endpoint"]
    
    if not token or not base_url:
        print("    ❌ Databricks configuration incomplete")
        return False
    
    try:
        # Test endpoint - using a simple prompt
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Build URL
        if endpoint_path.startswith("http"):
            url = endpoint_path
        else:
            url = f"{base_url.rstrip('/')}{endpoint_path}"
        
        data = {
            "messages": [
                {"role": "user", "content": "Test connection - respond with 'OK'"}
            ],
            "temperature": 0.0
        }
        
        timeout = databricks_config.get("timeout", 60)
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=timeout)
        
        if response.status_code == 200:
            print(f"    ✅ Databricks LLM connection successful")
            print(f"    📋 URL: {url}")
            print(f"    📋 Model: {databricks_config.get('model_name', 'Unknown')}")
            return True
        else:
            print(f"    ❌ Databricks LLM failed with status {response.status_code}")
            print(f"    📋 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"    ❌ Databricks LLM connection timeout (>{timeout}s)")
        return False
    except Exception as e:
        print(f"    ❌ Databricks LLM connection failed: {e}")
        return False

def check_gitlab_api():
    """Test GitLab API connectivity."""
    print("\n🦊 Testing GitLab API Connection...")
    
    token = os.getenv('GITLAB_API_TOKEN')
    
    if not token:
        print("    ❌ GitLab API token not set")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test with user endpoint
        response = requests.get("https://gitlab.com/api/v4/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"    ✅ GitLab API connection successful")
            print(f"    📋 User: {user_data.get('name', 'Unknown')}")
            return True
        else:
            print(f"    ❌ GitLab API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    ❌ GitLab API connection failed: {e}")
        return False

def check_runner_network():
    """Check basic network connectivity."""
    print("\n🌐 Testing Network Connectivity...")
    
    test_urls = [
        "https://gitlab.com",
        "https://dbc-3735add4-1cb6.cloud.databricks.com"  # Databricks base URL
    ]
    
    all_good = True
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code < 400:
                print(f"    ✅ {url} - accessible")
            else:
                print(f"    ⚠️  {url} - returned {response.status_code}")
                all_good = False
        except Exception as e:
            print(f"    ❌ {url} - failed: {e}")
            all_good = False
    
    return all_good

def main():
    """Main function to run all checks."""
    print("🚀 Local GitLab Runner Configuration Checker")
    print("=" * 60)
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Network Connectivity", check_runner_network),
        ("Database Connection", check_database_connection),
        ("Databricks LLM", check_databricks_llm),
        ("GitLab API", check_gitlab_api)
    ]
    
    results = {}
    
    for check_name, check_function in checks:
        try:
            results[check_name] = check_function()
        except Exception as e:
            print(f"    ❌ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    print("\n" + "=" * 60)
    print("📊 CONFIGURATION CHECK SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All checks passed! Your local runner is ready for AI code review.")
        print("\nNext steps:")
        print("1. Register the GitLab runner with tags: local-runner, ai-review")
        print("2. Create a test merge request to validate the pipeline")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above before proceeding.")
        print("\nRefer to local-runner-setup.md for detailed configuration instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
