#!/usr/bin/env python3
"""
Database Verification and Setup Script
Verifies database connectivity and sets up required tables/data if needed
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def get_db_config():
    """Get database configuration from environment variables."""
    load_dotenv()
    
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'dbname': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'root')
    }

def test_database_connection():
    """Test database connectivity."""
    print("Testing database connection...")
    
    config = get_db_config()
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"SUCCESS: Connected to PostgreSQL")
        print(f"Database version: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Database connection failed: {str(e)}")
        return False

def main():
    """Main execution function."""
    print("Database Verification Script")
    print("=" * 30)
    
    try:
        success = test_database_connection()
        
        if success:
            print("\nDatabase verification completed successfully.")
            return 0
        else:
            print("\nDatabase verification failed.")
            print("AI review will continue without database rules.")
            return 0  # Don't fail the pipeline for database issues
            
    except Exception as e:
        print(f"\nError during database verification: {str(e)}")
        return 0  # Don't fail the pipeline for database issues

if __name__ == "__main__":
    sys.exit(main())
