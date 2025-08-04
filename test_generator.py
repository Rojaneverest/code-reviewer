from rag.generator import generate_review

def test_model_prompt():
    """A simple test to manually prompt the review generation model."""
    # 1. Define a sample code snippet to review
    code_to_review = "SELECT * FROM customers;"

    # 2. Manually define a list of rules (mimicking the retriever's output)
    # Rule format: (rule_id, code_pattern, language, category, severity, title, description, last_updated_utc)
    manual_rules = [
        (1, 'SELECT *', 'SQL', 'Performance', 'Major', 'Avoid SELECT *', 'Use specific columns for better performance.', None),
        (2, 'LIKE ''%...', 'SQL', 'Performance', 'Major', 'Avoid leading wildcards in LIKE', 'Using a wildcard at the beginning of a LIKE pattern prevents the database from using an index.', None)
    ]

    print("--- Sending Prompt to Model ---")
    print(f"Code: {code_to_review}")
    print("Rules: Avoid SELECT *, Avoid leading wildcards")
    print("---------------------------------")

    # 3. Generate the review
    review = generate_review(code_to_review, manual_rules)

    # 4. Print the result
    print("\n--- Model Output ---")
    print(review)
    print("--- End of Output ---")

if __name__ == '__main__':
    test_model_prompt()
