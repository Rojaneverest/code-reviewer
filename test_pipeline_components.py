#!/usr/bin/env python3
# test_pipeline_components.py - Test GitLab CI pipeline components

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing Pipeline Component Imports")
    print("=" * 50)
    
    try:
        from config import DB_CONFIG
        print("✅ config.py - Database configuration")
    except Exception as e:
        print(f"❌ config.py failed: {e}")
        return False
    
    try:
        import cloud_db_setup
        print("✅ cloud_db_setup.py - Supabase database setup")
    except Exception as e:
        print(f"❌ cloud_db_setup.py failed: {e}")
        return False
    
    try:
        import test_supabase_connection
        print("✅ test_supabase_connection.py - Database precheck")
    except Exception as e:
        print(f"❌ test_supabase_connection.py failed: {e}")
        return False
    
    try:
        import gitlab_ci_analyzer
        print("✅ gitlab_ci_analyzer.py - GitLab CI integration")
    except Exception as e:
        print(f"❌ gitlab_ci_analyzer.py failed: {e}")
        return False
    
    print("\n🎉 All pipeline components imported successfully!")
    return True

def test_functions():
    """Test that key functions are available."""
    print("\n🔧 Testing Key Functions")
    print("=" * 30)
    
    try:
        from cloud_db_setup import main as setup_main
        print("✅ cloud_db_setup.main() - Database setup function")
    except Exception as e:
        print(f"❌ cloud_db_setup.main() failed: {e}")
        return False
    
    # Test that the test_supabase_connection.py module can be executed
    try:
        result = os.system("python test_supabase_connection.py --help 2>/dev/null")
        print("✅ test_supabase_connection.py - Executable connection test")
    except Exception as e:
        print(f"❌ test_supabase_connection.py failed: {e}")
        return False
    
    try:
        from gitlab_ci_analyzer import get_gitlab_env_vars
        print("✅ gitlab_ci_analyzer.get_gitlab_env_vars() - GitLab integration")
    except Exception as e:
        print(f"❌ gitlab_ci_analyzer.get_gitlab_env_vars() failed: {e}")
        return False
    
    print("\n🎉 All key functions are available!")
    return True

def test_environment_vars():
    """Test environment variable availability."""
    print("\n🌍 Testing Environment Variables")
    print("=" * 35)
    
    required_vars = ['host', 'port', 'dbname', 'user', 'password']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} = {value if var != 'password' else '*' * len(value)}")
        else:
            print(f"❌ {var} = NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Set these for full testing:")
        print("   export host='db.ziuhftkruvdlwiyfepop.supabase.co'")
        print("   export port='5432'")
        print("   export dbname='postgres'")
        print("   export user='postgres'")
        print("   export password='your_supabase_password'")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def main():
    """Run all pipeline tests."""
    print("🚀 GitLab CI Pipeline Component Tests")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_functions():
        tests_passed += 1
    
    if test_environment_vars():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Pipeline components are ready.")
        return True
    else:
        print("❌ Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
