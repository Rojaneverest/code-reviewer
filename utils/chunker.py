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
