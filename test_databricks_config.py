#!/usr/bin/env python3
"""
Test script for Databricks LLM configuration
Validates the updated configuration system and fallback mechanism
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_configuration():
    """Test the configuration loading."""
    print("🔧 Testing Configuration Loading...")
    
    try:
        from config import LLM_CONFIG
        print("✅ Configuration imported successfully")
        
        databricks_config = LLM_CONFIG["databricks"]
        lm_studio_config = LLM_CONFIG["lm_studio"]
        
        print(f"\n📋 Databricks Configuration:")
        print(f"  Enabled: {databricks_config['enabled']}")
        print(f"  Base URL: {databricks_config['base_url']}")
        print(f"  Endpoint: {databricks_config['endpoint']}")
        print(f"  Model: {databricks_config['model_name']}")
        print(f"  Timeout: {databricks_config['timeout']}s")
        
        print(f"\n📋 LM Studio Configuration:")
        print(f"  Enabled: {lm_studio_config['enabled']}")
        print(f"  API Base: {lm_studio_config['api_base']}")
        print(f"  Timeout: {lm_studio_config['timeout']}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_databricks_call():
    """Test calling the Databricks LLM."""
    print("\n🤖 Testing Databricks LLM Call...")
    
    try:
        from rag.generator import call_databricks_llm
        
        # Simple test prompt
        test_prompt = "Please respond with exactly 'Configuration Test Successful' and nothing else."
        
        print("  Calling Databricks LLM...")
        result = call_databricks_llm(test_prompt, temperature=0.0)
        
        if result:
            print(f"✅ Databricks LLM response received:")
            print(f"  Response: {result[:100]}{'...' if len(result) > 100 else ''}")
            return True
        else:
            print("❌ No response received from Databricks LLM")
            return False
            
    except Exception as e:
        print(f"❌ Databricks LLM test failed: {e}")
        return False

def test_fallback_mechanism():
    """Test the fallback mechanism."""
    print("\n🔄 Testing Fallback Mechanism...")
    
    try:
        from rag.generator import call_lm_studio_fallback
        
        # Test fallback (this will likely fail unless LM Studio is running)
        test_prompt = "Test fallback mechanism"
        
        print("  Testing LM Studio fallback...")
        result = call_lm_studio_fallback(test_prompt, temperature=0.0)
        
        if result:
            print(f"✅ LM Studio fallback working:")
            print(f"  Response: {result[:100]}{'...' if len(result) > 100 else ''}")
            return True
        else:
            print("⚠️  LM Studio fallback not available (expected if not running locally)")
            return False
            
    except Exception as e:
        print(f"ℹ️  LM Studio fallback test: {e}")
        return False

def test_full_review():
    """Test a full code review."""
    print("\n📝 Testing Full Code Review...")
    
    try:
        from rag.generator import generate_review
        
        # Simple SQL test code
        test_code = """
        SELECT * 
        FROM users 
        WHERE password = 'admin123'
        """
        
        test_rules = {
            'bad_practices': [
                {
                    'id': 'test-1',
                    'title': 'Hardcoded Password',
                    'severity': 'Critical',
                    'description': 'Never hardcode passwords in SQL queries'
                }
            ],
            'good_practices': []
        }
        
        print("  Running code review...")
        result = generate_review(test_code, test_rules, "Vector Search")
        
        if result:
            print(f"✅ Code review completed:")
            print(f"  Issues found: {result.get('issues_found', 0)}")
            if result.get('issues'):
                for issue in result['issues']:
                    print(f"    - {issue.get('severity', 'Unknown')}: {issue.get('suggestion', 'No suggestion')[:60]}...")
            return True
        else:
            print("❌ Code review failed")
            return False
            
    except Exception as e:
        print(f"❌ Code review test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Databricks Configuration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("Databricks LLM Call", test_databricks_call),
        ("Fallback Mechanism", test_fallback_mechanism),
        ("Full Code Review", test_full_review)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        try:
            results[test_name] = test_function()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Databricks configuration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the configuration and environment variables.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
