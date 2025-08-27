#!/usr/bin/env python3
# cloud_db_setup.py - Initialize Supabase cloud database with SQL rules and vectorization

import psycopg2
import os
import sys
import subprocess
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from config import DB_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to Supabase cloud database."""
    logger.info("🔌 Testing Supabase connection...")
    logger.info(f"Host: {DB_CONFIG.get('host', 'Not set')}")
    logger.info(f"Port: {DB_CONFIG.get('port', 'Not set')}")
    logger.info(f"Database: {DB_CONFIG.get('dbname', 'Not set')}")
    logger.info(f"User: {DB_CONFIG.get('user', 'Not set')}")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"✅ Connected to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.error("Please check your Supabase credentials and network connectivity")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def setup_database():
    """Setup the database with rules table and initial data."""
    logger.info("🔧 Setting up database schema and data...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create the rules table with vector column for embeddings
        logger.info("📋 Creating rules table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id SERIAL PRIMARY KEY,
                code_pattern TEXT NOT NULL,
                language TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                example_snippet TEXT,
                practice_type TEXT NOT NULL DEFAULT 'bad',
                last_updated_utc TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                vector FLOAT[],  -- Stores CodeT5 embeddings
                UNIQUE (language, title)
            );
        """)
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM rules;")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            logger.info(f"📊 Database already has {existing_count} rules. Skipping data insertion.")
        else:
            # Load and execute the insert_rules.sql file
            logger.info("📄 Loading rules from insert_rules.sql...")
            sql_file_path = os.path.join(project_root, 'database', 'insert_rules.sql')
            
            if os.path.exists(sql_file_path):
                with open(sql_file_path, 'r') as f:
                    sql_content = f.read()
                    cursor.execute(sql_content)
                
                # Verify insertion
                cursor.execute("SELECT COUNT(*) FROM rules;")
                rule_count = cursor.fetchone()[0]
                logger.info(f"✅ Successfully inserted {rule_count} rules")
            else:
                logger.error(f"❌ SQL file not found: {sql_file_path}")
                return False
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup error: {e}")
        return False

def run_vectorization():
    """Run the rule vectorization process."""
    logger.info("🤖 Starting rule vectorization process...")
    
    try:
        # Check if rules are already vectorized
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM rules WHERE vector IS NOT NULL;")
        vectorized_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rules;")
        total_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        if vectorized_count == total_count and total_count > 0:
            logger.info(f"✅ All {total_count} rules are already vectorized. Skipping vectorization.")
            return True
        
        logger.info(f"📊 Found {total_count - vectorized_count} rules to vectorize out of {total_count} total...")
        
        # Run the vectorization script
        rag_script = os.path.join(project_root, 'rag', 'vectorize_rules.py')
        
        if not os.path.exists(rag_script):
            logger.error(f"❌ Vectorization script not found: {rag_script}")
            return False
        
        logger.info("🔄 Running vectorization script...")
        result = subprocess.run([sys.executable, rag_script], 
                              capture_output=True, text=True, check=True,
                              cwd=project_root)
        
        if result.stdout:
            logger.info(f"Vectorization output: {result.stdout.strip()}")
        
        logger.info("✅ Rule vectorization completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error during vectorization: {e}")
        if e.stderr:
            logger.error(f"Vectorization error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during vectorization: {e}")
        return False

def main():
    """Main setup function for Supabase cloud database."""
    logger.info("🌟 Supabase Cloud Database Setup for SQL Code Review")
    logger.info("=" * 60)
    
    # Step 1: Test connection
    logger.info("Step 1: Testing database connection...")
    if not test_connection():
        logger.error("❌ Failed to connect to Supabase database")
        return False
    
    # Step 2: Setup database schema and data
    logger.info("Step 2: Setting up database schema and data...")
    if not setup_database():
        logger.error("❌ Failed to setup database")
        return False
    
    # Step 3: Run vectorization
    logger.info("Step 3: Running rule vectorization...")
    if not run_vectorization():
        logger.error("❌ Failed to vectorize rules")
        return False
    
    logger.info("🎉 Supabase database setup completed successfully!")
    logger.info("✅ Database ready for SQL code review in GitLab CI!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)