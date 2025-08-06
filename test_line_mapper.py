from utils.line_mapper import map_sql_statements_to_lines

# Define the path to the test SQL file
file_path = 'test_files/test_no_match.sql'

print(f"--- Testing line mapper on {file_path} ---")

# Read the content of the file
try:
    with open(file_path, 'r') as f:
        file_content = f.read()
except FileNotFoundError:
    print(f"Error: Test file not found at {file_path}")
    exit()

# Get the list of (statement, line_number) tuples
mapped_statements = map_sql_statements_to_lines(file_content)

# Print the results for verification
if not mapped_statements:
    print("No statements were mapped.")
else:
    print(f"Found {len(mapped_statements)} statements:")
    for i, (statement, line_number) in enumerate(mapped_statements, 1):
        print(f"  Syntax #{i}: Starts at Line {line_number}")
        print(f"    Statement: {statement[:100].replace('\n', ' ')}...")

print("--- End of Test ---")
