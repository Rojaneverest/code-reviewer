import psycopg2
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import DB_CONFIG

def setup_enhanced_database():
    """Sets up the PostgreSQL database with enhanced vector columns for multi-vector approach."""
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Drop the rules table if it exists
        print('Dropping table "rules" if it exists...')
        cursor.execute("DROP TABLE IF EXISTS rules;")

        # Create the enhanced rules table with multiple vector columns
        print('Creating enhanced table "rules" with multiple vector types...')
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
            vector FLOAT[],  -- Original combined embedding (backward compatibility)
            sql_pattern_vector FLOAT[],  -- SQL structure/pattern focused embedding
            semantic_vector FLOAT[],  -- Semantic intent focused embedding
            hybrid_vector FLOAT[],  -- Hybrid approach embedding
            UNIQUE (language, title)
        );
        """)

        # Insert initial data from SQL file
        print('Inserting initial data from "database/insert_rules.sql"...')
        sql_file_path = os.path.join(os.path.dirname(__file__), 'insert_rules.sql')
        with open(sql_file_path, 'r') as f:
            cursor.execute(f.read())

        conn.commit()
        print('Enhanced database setup completed successfully.')
        
        # Show table structure
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'rules' ORDER BY ordinal_position;")
        columns = cursor.fetchall()
        print('\nTable structure:')
        for col_name, col_type in columns:
            print(f"  {col_name}: {col_type}")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"General error: {e}")
    finally:
        if conn:
            conn.close()

def add_vector_columns_to_existing():
    """Add new vector columns to existing rules table without dropping it."""
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check if new columns already exist
        cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'rules' AND column_name IN ('sql_pattern_vector', 'semantic_vector', 'hybrid_vector');
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        columns_to_add = ['sql_pattern_vector', 'semantic_vector', 'hybrid_vector']
        
        for column in columns_to_add:
            if column not in existing_columns:
                print(f'Adding column {column}...')
                cursor.execute(f"ALTER TABLE rules ADD COLUMN {column} FLOAT[];")
            else:
                print(f'Column {column} already exists, skipping...')

        conn.commit()
        print('Vector columns added successfully.')
        
        # Show updated table structure
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'rules' ORDER BY ordinal_position;")
        columns = cursor.fetchall()
        print('\nUpdated table structure:')
        for col_name, col_type in columns:
            print(f"  {col_name}: {col_type}")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"General error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--add-columns":
        add_vector_columns_to_existing()
    else:
        setup_enhanced_database()
