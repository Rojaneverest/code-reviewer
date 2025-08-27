#!/usr/bin/env python3
# setup_ci_database.py - Initialize PostgreSQL service with SQL rules for GitLab CI

import psycopg2
import os
import sys
import time
import subprocess

def wait_for_postgres():
    """Wait for PostgreSQL service to be ready."""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            conn = psycopg2.connect(
                host=os.getenv('host', 'postgres'),
                database=os.getenv('dbname', 'rules'),
                user=os.getenv('user', 'postgres'),
                password=os.getenv('password', 'root'),
                port=os.getenv('port', '5432')
            )
            conn.close()
            print("✅ PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError:
            print(f"⏳ Waiting for PostgreSQL... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
    
    print("❌ PostgreSQL failed to start")
    return False

def setup_database():
    """Initialize database with SQL rules using existing insert_rules.sql and vectorize them."""
    print("🔧 Setting up CI database with SQL rules...")
    
    if not wait_for_postgres():
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('host', 'postgres'),
            database=os.getenv('dbname', 'rules'),
            user=os.getenv('user', 'postgres'),
            password=os.getenv('password', 'root'),
            port=os.getenv('port', '5432')
        )
        
        cursor = conn.cursor()
        
        print("📋 Creating rules table...")
        # Create the rules table with vector column for embeddings
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
        
        print("📄 Loading rules from insert_rules.sql...")
        # Load and execute the existing insert_rules.sql file
        sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'insert_rules.sql')
        
        if not os.path.exists(sql_file_path):
            print(f"❌ SQL file not found: {sql_file_path}")
            sys.exit(1)
            
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
            cursor.execute(sql_content)
        
        conn.commit()
        print("✅ Rules inserted successfully!")
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM rules;")
        rule_count = cursor.fetchone()[0]
        print(f"📊 Inserted {rule_count} rules into database")
        
        # Close database connection before running vectorization
        cursor.close()
        conn.close()
        
        print("🧠 Running rule vectorization...")
        # Run the vectorization script
        vectorize_script = os.path.join(os.path.dirname(__file__), 'rag', 'vectorize_rules.py')
        
        if not os.path.exists(vectorize_script):
            print(f"❌ Vectorization script not found: {vectorize_script}")
            sys.exit(1)
        
        # Set environment variables for the vectorization script
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(__file__)
        
        # Run vectorize_rules.py
        result = subprocess.run([sys.executable, vectorize_script], 
                              capture_output=True, text=True, 
                              cwd=os.path.dirname(__file__), env=env)
        
        if result.returncode == 0:
            print("✅ Rule vectorization completed successfully!")
            if result.stdout:
                print("📊 Vectorization output:")
                print(result.stdout)
        else:
            print("❌ Rule vectorization failed!")
            print("Error output:")
            print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
            sys.exit(1)
            
        print("🎉 Database setup and vectorization completed!")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 GitLab CI Database Setup")
    print("=" * 50)
    setup_database()

