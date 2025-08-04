import sqlparse

def chunk_sql_file(file_content):
    """Splits a SQL file into statements, tracking the starting line number of each."""
    statements = []
    # Use sqlparse.parse to get individual statements
    parsed = sqlparse.parse(file_content)
    line_offset = 0
    for stmt in parsed:
        if not str(stmt).strip():
            continue
        # Find the line number of the start of the statement
        stmt_str = str(stmt).strip()
        # A simple way to find the line number is to count newlines
        # in the content before the statement starts.
        # This is an approximation.
        temp_content = file_content[line_offset:]
        stmt_start_pos = temp_content.find(stmt_str)
        line_number = temp_content[:stmt_start_pos].count('\n') + 1

        statements.append((stmt_str, line_offset + line_number))
        line_offset += stmt_start_pos + len(stmt_str)

    return statements

def chunk_pyspark_file(file_content):
    """Splits a PySpark file into chunks, tracking the starting line number of each."""
    chunks = []
    current_chunk = []
    start_line = 1
    for i, line in enumerate(file_content.splitlines(), 1):
        if not line.strip() and current_chunk:
            chunks.append(("\n".join(current_chunk), start_line))
            current_chunk = []
        elif line.strip():
            if not current_chunk:
                start_line = i
            current_chunk.append(line)
    if current_chunk:
        chunks.append(("\n".join(current_chunk), start_line))
    return chunks

def chunk_code(file_path, file_content):
    """Detects the language and chunks the code accordingly."""
    if file_path.endswith('.sql'):
        return chunk_sql_file(file_content)
    elif file_path.endswith('.py'):
        return chunk_pyspark_file(file_content)
    else:
        return [(file_content, 1)] # Treat unsupported files as a single chunk
