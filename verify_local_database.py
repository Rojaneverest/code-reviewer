#!/usr/bin/env python3
"""
Local Database Setup Verification Script
Verifies that the local PostgreSQL database is properly configured for the AI code reviewer
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database_connection():
    """Test local PostgreSQL database connectivity."""
    print("🗄️  Testing Local PostgreSQL Database Connection...")
    
    # Use local defaults, override any existing environment variables
    config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'rules',
        'user': 'postgres',
        'password': 'root'
    }
    
    # Allow environment variables to override defaults if explicitly set for local use
    if os.getenv('host') == 'localhost':
        config['host'] = os.getenv('host', 'localhost')
        config['port'] = os.getenv('port', '5432')
        config['database'] = os.getenv('dbname', 'rules')
        config['user'] = os.getenv('user', 'postgres')
        config['password'] = os.getenv('password', 'root')
    
    print(f"  Connecting to: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"  ✅ Connection successful")
        print(f"  📋 PostgreSQL version: {version}")
        
        # Check if rules table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'rules'
            );
        """)
        rules_table_exists = cursor.fetchone()[0]
        print(f"  📋 Rules table exists: {'Yes' if rules_table_exists else 'No'}")
        
        if rules_table_exists:
            # Count rules in the table
            cursor.execute("SELECT COUNT(*) FROM rules;")
            rule_count = cursor.fetchone()[0]
            print(f"  📋 Number of rules: {rule_count}")
            
            if rule_count > 0:
                # Show a sample rule
                cursor.execute("SELECT id, title, rule_type FROM rules LIMIT 1;")
                sample_rule = cursor.fetchone()
                print(f"  📋 Sample rule: ID={sample_rule[0]}, Title='{sample_rule[1]}', Type='{sample_rule[2]}'")
        else:
            print(f"  ⚠️  Rules table not found. Run 'python database/setup_db.py' to create it.")
        
        cursor.close()
        conn.close()
        
        return rules_table_exists
        
    except psycopg2.OperationalError as e:
        print(f"  ❌ Connection failed: {e}")
        print(f"  💡 Make sure PostgreSQL is running locally and the database 'rules' exists")
        print(f"  💡 Check your database configuration:")
        print(f"     Host: {config['host']}")
        print(f"     Port: {config['port']}")
        print(f"     Database: {config['database']}")
        print(f"     User: {config['user']}")
        print(f"  💡 To create database: psql -U postgres -c 'CREATE DATABASE rules;'")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def setup_database():
    """Set up the database schema and rules."""
    print("\n🔧 Setting up database schema and rules...")
    
    try:
        # Import and run the database setup
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database.setup_db import main as setup_main
        
        print("  Running database setup...")
        setup_main()
        print("  ✅ Database setup completed")
        return True
        
    except ImportError as e:
        print(f"  ❌ Failed to import database setup module: {e}")
        print(f"  💡 Make sure you're in the correct directory and database/setup_db.py exists")
        return False
    except Exception as e:
        print(f"  ❌ Database setup failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Local Database Setup Verification")
    print("=" * 50)
    
    # Test database connection first
    db_connected = check_database_connection()
    
    if not db_connected:
        print("\n❌ Database connection failed. Please check your PostgreSQL installation and configuration.")
        print("\n📋 Steps to fix:")
        print("1. Ensure PostgreSQL is installed and running")
        print("2. Create the 'rules' database if it doesn't exist")
        print("3. Check your environment variables or use defaults (localhost:5432)")
        return 1
    
    # Check if rules table exists and has data
    try:
        # Use local defaults
        config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'rules',
            'user': 'postgres',
            'password': 'root'
        }
        
        # Allow environment variables to override defaults if explicitly set for local use
        if os.getenv('host') == 'localhost':
            config['host'] = os.getenv('host', 'localhost')
            config['port'] = os.getenv('port', '5432')
            config['database'] = os.getenv('dbname', 'rules')
            config['user'] = os.getenv('user', 'postgres')
            config['password'] = os.getenv('password', 'root')
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM rules;")
        rule_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        if rule_count == 0:
            print("\n⚠️  Rules table is empty. Setting up rules...")
            if setup_database():
                print("✅ Database setup completed successfully!")
            else:
                print("❌ Database setup failed.")
                return 1
        else:
            print(f"\n✅ Database is properly configured with {rule_count} rules!")
            
    except Exception as e:
        print(f"\n❌ Error checking rules: {e}")
        return 1
    
    print("\n🎉 Local database verification completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure Databricks environment variables")
    print("2. Run: python check_local_runner.py")
    print("3. Test with a merge request")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
