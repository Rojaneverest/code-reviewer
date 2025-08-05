import sqlparse

def map_sql_statements_to_lines(sql_content):
    """
    Parses SQL content, strips comments, and maps statements to their original starting line numbers.
    This version is designed to be more robust against blank lines and formatting differences.
    """
    statements = []
    try:
        # Use sqlparse.format and then split. This is more reliable for isolating statements.
        stripped_sql = sqlparse.format(sql_content, strip_comments=True)
        statements = sqlparse.split(stripped_sql)
    except Exception as e:
        print(f"Could not parse SQL with sqlparse, falling back to simple split: {e}")
        statements = [s for s in sql_content.split(';') if s.strip()]

    original_lines = sql_content.splitlines()
    clean_original_lines = [line.strip() for line in original_lines]

    chunks = []
    current_line_index = 0

    for stmt in statements:
        stmt_clean = stmt.strip()
        if not stmt_clean:
            continue

        # Get the first non-empty line of the statement to use as a search key.
        stmt_first_line = ""
        for line in stmt_clean.splitlines():
            if line.strip():
                stmt_first_line = line.strip()
                break
        
        if not stmt_first_line:
            continue

        # Search for the first line of the statement in the original file content.
        for i in range(current_line_index, len(clean_original_lines)):
            if stmt_first_line in clean_original_lines[i]:
                # We found the starting line.
                chunks.append((stmt_clean, i + 1))  # i + 1 for 1-based line number
                current_line_index = i + 1  # Start next search from the next line
                break


    return chunks
