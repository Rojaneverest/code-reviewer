#!/usr/bin/env python3
# setup_ci_database.py - Initialize PostgreSQL service with SQL rules for GitLab CI

import psycopg2
import os
import sys
import time
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_config():
    """Get database configuration from environment variables."""
    return {
        "dbname": os.getenv("dbname", "rules"),
        "user": os.getenv("user", "postgres"),
        "password": os.getenv("password", "root"),
        "host": os.getenv("host", "postgres"),
        "port": os.getenv("port", "5432")
    }

def wait_for_postgres(max_attempts=60, wait_interval=3):
    """Wait for PostgreSQL service to be ready with better error handling."""
    db_config = get_db_config()
    
    logger.info(f"Waiting for PostgreSQL at {db_config['host']}:{db_config['port']}...")
    
    for attempt in range(max_attempts):
        try:
            # Try to connect to the default postgres database first
            test_config = db_config.copy()
            test_config["dbname"] = "postgres"  # Connect to default DB first
            
            conn = psycopg2.connect(**test_config)
            conn.close()
            logger.info("✅ PostgreSQL is ready!")
            return True
            
        except psycopg2.OperationalError as e:
            logger.info(f"⏳ Waiting for PostgreSQL... (attempt {attempt + 1}/{max_attempts})")
            logger.debug(f"Connection error: {e}")
            
            # Check if it's a network connectivity issue
            if attempt == 10:
                try:
                    # Try to ping the postgres service
                    result = subprocess.run(['ping', '-c', '1', db_config['host']], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode != 0:
                        logger.error(f"Cannot reach PostgreSQL host: {db_config['host']}")
                        logger.error("This might be a GitLab CI service configuration issue")
                except Exception as ping_error:
                    logger.warning(f"Could not ping host: {ping_error}")
            
            time.sleep(wait_interval)
    
    logger.error("❌ PostgreSQL failed to start within the timeout period")
    return False

def create_database_if_not_exists():
    """Create the target database if it doesn't exist."""
    db_config = get_db_config()
    
    try:
        # Connect to default postgres database to create our target database
        default_config = db_config.copy()
        default_config["dbname"] = "postgres"
        
        conn = psycopg2.connect(**default_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_config["dbname"],))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database: {db_config['dbname']}")
            cursor.execute(f'CREATE DATABASE "{db_config["dbname"]}"')
        else:
            logger.info(f"Database {db_config['dbname']} already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def execute_sql_file(file_path):
    """Execute SQL file using psql command."""
    db_config = get_db_config()
    
    if not os.path.exists(file_path):
        logger.error(f"SQL file not found: {file_path}")
        return False
    
    try:
        # Use psql to execute the SQL file
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']
        
        cmd = [
            'psql',
            '-h', db_config['host'],
            '-p', str(db_config['port']),
            '-U', db_config['user'],
            '-d', db_config['dbname'],
            '-f', file_path,
            '-v', 'ON_ERROR_STOP=1'  # Stop on first error
        ]
        
        logger.info(f"Executing SQL file: {file_path}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        
        if result.stdout:
            logger.info(f"SQL execution output: {result.stdout}")
        
        logger.info("✅ SQL file executed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing SQL file: {e}")
        if e.stderr:
            logger.error(f"SQL error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error executing SQL file: {e}")
        return False

def run_vectorization():
    """Run the rule vectorization process."""
    try:
        logger.info("🤖 Starting rule vectorization process...")
        
        # Add the project root to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        rag_script = os.path.join(project_root, 'rag', 'vectorize_rules.py')
        
        if not os.path.exists(rag_script):
            logger.error(f"Vectorization script not found: {rag_script}")
            return False
        
        # Run the vectorization script
        result = subprocess.run([sys.executable, rag_script], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout:
            logger.info(f"Vectorization output: {result.stdout}")
        
        logger.info("✅ Rule vectorization completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during vectorization: {e}")
        if e.stderr:
            logger.error(f"Vectorization error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during vectorization: {e}")
        return False

def setup_database():
    """Main database setup function."""
    logger.info("🚀 GitLab CI Database Setup")
    logger.info("=" * 50)
    
    # Step 1: Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        logger.error("Failed to connect to PostgreSQL service")
        return False
    
    # Step 2: Create database if it doesn't exist
    if not create_database_if_not_exists():
        logger.error("Failed to create database")
        return False
    
    # Step 3: Execute the SQL rules file
    sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'insert_rules.sql')
    if not execute_sql_file(sql_file_path):
        logger.error("Failed to execute SQL rules file")
        return False
    
    # Step 4: Run vectorization
    if not run_vectorization():
        logger.error("Failed to vectorize rules")
        return False
    
    logger.info("🎉 Database setup completed successfully!")
    return True

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)

