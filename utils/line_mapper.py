import sqlparse
import re

def map_sql_statements_to_lines(sql_content):
    """
    Parses SQL content and maps statements to their original starting line numbers.
    Uses character position tracking for more accurate line mapping.
    """
    statements = []
    try:
        # Parse without stripping comments initially to preserve structure
        parsed = sqlparse.parse(sql_content)
        statements = [str(stmt) for stmt in parsed if str(stmt).strip()]
    except Exception as e:
        print(f"Could not parse SQL with sqlparse, falling back to simple split: {e}")
        statements = [s for s in sql_content.split(';') if s.strip()]

    original_lines = sql_content.splitlines()
    chunks = []
    search_start_pos = 0  # Track character position instead of just line index

    for stmt in statements:
        stmt_clean = stmt.strip()
        if not stmt_clean:
            continue

        # Get the first meaningful SQL line (skip comments and empty lines)
        stmt_lines = stmt_clean.splitlines()
        stmt_first_sql_line = ""
        
        for line in stmt_lines:
            line_stripped = line.strip()
            # Skip empty lines and comment lines
            if line_stripped and not line_stripped.startswith('--'):
                # Clean up the line for matching
                stmt_first_sql_line = re.sub(r'\s+', ' ', line_stripped).strip()
                break
        
        if not stmt_first_sql_line:
            continue

        # Find the position of this statement in the original content
        # Start searching from where we left off
        remaining_content = sql_content[search_start_pos:]
        
        # Look for the first significant word of the SQL statement
        first_word = stmt_first_sql_line.split()[0].upper()
        
        # Find all potential matches in the remaining content
        pattern = r'\b' + re.escape(first_word) + r'\b'
        matches = list(re.finditer(pattern, remaining_content, re.IGNORECASE))
        
        found = False
        for match in matches:
            match_pos = search_start_pos + match.start()
            
            # Convert character position to line number
            content_up_to_match = sql_content[:match_pos]
            line_number = content_up_to_match.count('\n') + 1
            
            # Get the actual line content at this position
            if line_number <= len(original_lines):
                actual_line = original_lines[line_number - 1].strip()
                
                # Skip if this line is a comment
                if actual_line.startswith('--') or not actual_line:
                    continue
                
                # Check if this line matches our expected pattern
                normalized_actual = re.sub(r'\s+', ' ', actual_line).strip()
                if normalized_actual.upper().startswith(first_word.upper()):
                    # Clean the statement by removing comments for the final output
                    clean_stmt = sqlparse.format(stmt_clean, strip_comments=True).strip()
                    chunks.append((clean_stmt, line_number))
                    
                    # Update search position to after this statement
                    # Find the end of this statement (look for semicolon or end of content)
                    stmt_end = sql_content.find(';', match_pos)
                    if stmt_end != -1:
                        search_start_pos = stmt_end + 1
                    else:
                        search_start_pos = match_pos + len(stmt_first_sql_line)
                    
                    found = True
                    break
        
        if not found:
            print(f"Warning: Could not find line mapping for statement: {stmt_first_sql_line[:50]}...")

    return chunks