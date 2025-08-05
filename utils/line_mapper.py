import sqlparse

def map_sql_statements_to_lines(file_content):
    """
    Parses a SQL file to map each statement to its starting line number, as per the user's suggestion.

    Args:
        file_content (str): The content of the SQL file.

    Returns:
        list: A list of tuples, where each tuple contains the statement text (str) and its starting line number (int).
    """
    statements_with_lines = []
    parsed_statements = sqlparse.parse(file_content)
    current_pos = 0

    for stmt in parsed_statements:
        # Reconstruct the statement without comments
        clean_tokens = []
        for token in stmt.flatten():
            if not isinstance(token.parent, sqlparse.sql.Comment) and not token.is_whitespace:
                clean_tokens.append(str(token))
        
        clean_stmt_text = " ".join(clean_tokens).strip()

        if not clean_stmt_text:
            continue

        # Find the start of the original, un-commented statement text
        original_stmt_text = str(stmt).strip()
        try:
            original_stmt_start_pos = file_content.find(original_stmt_text, current_pos)
            if original_stmt_start_pos == -1:
                continue

            # Now, find the start of the *clean* statement within the original block
            clean_stmt_start_pos = original_stmt_text.find(clean_tokens[0])
            
            # The absolute position of the clean statement
            absolute_pos = original_stmt_start_pos + clean_stmt_start_pos
            
            # Calculate the line number
            line_number = file_content[:absolute_pos].count('\n') + 1
            statements_with_lines.append((clean_stmt_text, line_number))
            
            # Update current_pos to the end of the original statement block
            current_pos = original_stmt_start_pos + len(original_stmt_text)
        except (ValueError, IndexError):
            continue
            
    return statements_with_lines
