import requests
import json
from dotenv import load_dotenv
import os
import sys

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_CONFIG

load_dotenv()

def call_databricks_llm(prompt, temperature=0.0):
    """
    Call Databricks LLM endpoint with flexible configuration.
    Falls back to LM Studio if Databricks is not configured.
    """
    databricks_config = LLM_CONFIG["databricks"]
    
    # Check if Databricks is configured and enabled
    if not databricks_config["enabled"] or not databricks_config["token"]:
        print("Databricks not configured, attempting fallback to LM Studio...")
        return call_lm_studio_fallback(prompt, temperature)
    
    headers = {
        "Authorization": f"Bearer {databricks_config['token']}",
        "Content-Type": "application/json"
    }
    
    # Build the URL from configuration
    base_url = databricks_config["base_url"]
    endpoint_path = databricks_config.get("endpoint", "/serving-endpoints/databricks-claude-sonnet-4/invocations")
    
    # Handle both full URLs and base URLs
    if endpoint_path.startswith("http"):
        url = endpoint_path
    else:
        url = f"{base_url.rstrip('/')}{endpoint_path}"
    
    data = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        if response.status_code == 200:
            result = response.json()
            # Extract the text content from the response
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0]["message"]
                if "content" in message and isinstance(message["content"], list):
                    # Extract text from the content array
                    for content_item in message["content"]:
                        if content_item.get("type") == "text":
                            return content_item.get("text", "")
                elif "content" in message and isinstance(message["content"], str):
                    # Handle if content is a string (fallback)
                    return message["content"]
            return None
        else:
            print(f"Databricks LLM Error: {response.status_code} - {response.text}")
            print("Attempting fallback to LM Studio...")
            return call_lm_studio_fallback(prompt, temperature)
    except Exception as e:
        print(f"Error connecting to Databricks LLM: {e}")
        print("Attempting fallback to LM Studio...")
        return call_lm_studio_fallback(prompt, temperature)

def call_lm_studio_fallback(prompt, temperature=0.0):
    """
    Fallback to LM Studio when Databricks is unavailable.
    """
    lm_studio_config = LLM_CONFIG["lm_studio"]
    
    if not lm_studio_config["enabled"]:
        print("Both Databricks and LM Studio are unavailable. Please configure at least one LLM endpoint.")
        return None
    
    try:
        import openai
        
        # Configure OpenAI client for LM Studio
        client = openai.OpenAI(
            base_url=lm_studio_config["api_base"],
            api_key=lm_studio_config["api_key"]
        )
        
        response = client.chat.completions.create(
            model="local-model",  # LM Studio uses this as placeholder
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            timeout=60
        )
        
        return response.choices[0].message.content
        
    except ImportError:
        print("OpenAI library not installed. Install with: pip install openai")
        return None
    except Exception as e:
        print(f"Error connecting to LM Studio: {e}")
        return None

def generate_review(code_chunk, rules, retrieval_method="Vector Search"):
    """Generates a code review in a structured JSON format by calling the Databricks model."""
    
    # Add line numbers to the code chunk for clarity
    def add_line_numbers_to_chunk(chunk):
        """Add line numbers to code chunk to make line references clear to LLM."""
        numbered_lines = []
        for i, line in enumerate(chunk.splitlines(), 1):
            numbered_lines.append(f"{i:2d}: {line}")
        return "\n".join(numbered_lines)
    
    numbered_code_chunk = add_line_numbers_to_chunk(code_chunk)
    
    # Prepare the bad practices section of the prompt
    bad_practices_text = "\n".join([
        f"- {rule['title']} (Rule ID: {rule['id']}, Severity: {rule['severity']}): {rule['description']}"
        for rule in rules.get('bad_practices', [])
    ]) if rules.get('bad_practices') else "None"

    # Prepare the good practices section of the prompt
    good_practices_text = "\n".join([
        f"- {rule['title']} (Rule ID: {rule['id']}): {rule['description']}"
        for rule in rules.get('good_practices', [])
    ]) if rules.get('good_practices') else "None"

    # Default temperature for deterministic output
    temperature = 0.0

    # Handle database unavailable scenarios - fallback to AI analysis
    if retrieval_method in ["Database Unavailable - AI Fallback", "Rule Retrieval Failed - AI Fallback", "Error"]:
        temperature = 0.75
        prompt = f"""You are a highly intelligent SQL code review assistant. The rule-based retrieval system is currently unavailable (database connection issues), so you must rely entirely on your extensive knowledge of SQL best practices to conduct a thorough review.

**Code to Review (with line numbers for your reference):**
```
{numbered_code_chunk}
```

**CRITICAL:** When reporting issues, use the line numbers shown in the code above (1-{len(code_chunk.splitlines())}). Do NOT try to calculate or guess other line numbers.

**IMPORTANT - SELECT * GUIDELINES:**
- DO NOT flag "SELECT *" as an issue when it's used in:
  * CREATE VIEW or CREATE TEMP VIEW statements (data loading/transformation)
  * SELECT * FROM (subquery) where the subquery explicitly lists specific columns
  * Data pipeline operations, ETL processes, or data movement between tables
  * Any context where the columns are already well-defined in an inner query
- ONLY flag "SELECT *" when it's used directly against base tables without column specification in application queries

**CRITICAL - SUGGESTION FORMATTING:**
- In your `suggestion` text, DO NOT mention specific line numbers (like "line 5", "lines 2-3", etc.)
- Instead, refer to code elements by their content (e.g., "the COALESCE expression", "the WHERE clause", "the JOIN operation")
- Focus on describing WHAT the issue is and HOW to fix it, not WHERE it appears

**Task:**
1.  **Analyze the code comprehensively using your knowledge.** Look for common SQL anti-patterns, performance issues, security vulnerabilities, and maintainability concerns.
2.  **Focus on practical, actionable feedback.** Prioritize issues that could impact performance, security, or code maintainability.
3.  **Be concise and group related feedback.** If multiple suggestions apply to the same issue, combine them into a single, comprehensive suggestion. Aim to provide a maximum of three distinct, high-impact suggestions for the code chunk.
4.  If you identify any issues, create a JSON object describing them. Your response MUST be a single, valid JSON object.
5.  For each issue, provide **only** these three keys: `line_number` (use the numbers shown in the code above), `severity` (use "AI Generated Suggestion"), and `suggestion`. **Do not include a `rule_id` or any other keys.**
6.  If you find no issues, you MUST return this exact JSON object: `{{"issues_found": 0, "issues": []}}`

**Example of a valid response:**
```json
{{
  "issues_found": 1,
  "issues": [
    {{
      "line_number": 5,
      "severity": "AI Generated Suggestion",
      "suggestion": "Consider replacing the correlated subquery with an INNER JOIN for potentially better performance, as it can leverage hash joins more effectively."
    }}
  ]
}}
```

JSON Response:"""

    # Dynamically construct the prompt based on the retrieval method
    elif retrieval_method == "Regex Match":
        prompt = f"""You are a precise code review assistant. A code snippet has been identified as potentially violating one or more bad practices via direct Regex Matches.

**Bad Practices Found by Regex:**
{bad_practices_text}

**Code to Review (with line numbers for your reference):**
```
{numbered_code_chunk}
```

**CRITICAL:** When reporting issues, use the line numbers shown in the code above (1-{len(code_chunk.splitlines())}). Do NOT try to calculate or guess other line numbers.

**IMPORTANT - SELECT * GUIDELINES:**
- DO NOT flag "SELECT *" as an issue when it's used in:
  * CREATE VIEW or CREATE TEMP VIEW statements (data loading/transformation)
  * SELECT * FROM (subquery) where the subquery explicitly lists specific columns
  * Data pipeline operations, ETL processes, or data movement between tables
  * Any context where the columns are already well-defined in an inner query
- ONLY flag "SELECT *" when it's used directly against base tables without column specification in application queries

**CRITICAL - SUGGESTION FORMATTING:**
- In your `suggestion` text, DO NOT mention specific line numbers (like "line 5", "lines 2-3", etc.)
- Instead, refer to code elements by their content (e.g., "the COALESCE expression", "the WHERE clause", "the JOIN operation")
- Focus on describing WHAT the issue is and HOW to fix it, not WHERE it appears

**Task:**
1.  Your task is to review the code and confirm each violation from the list of 'Bad Practices Found by Regex'.
2.  Your response MUST be a single, valid JSON object. The JSON should contain a list of all confirmed issues.
3.  For each issue, provide **only** these four keys: `line_number` (use the numbers shown in the code above), `severity`, `rule_id`, and `suggestion`. **Do not add any other keys.**
4.  If you cannot confirm any of the violations, you MUST return this exact JSON object: `{{"issues_found": 0, "issues": []}}`

JSON Response:"""
    else:  # Vector Search, Hybrid Match, No Matches
        if rules.get('bad_practices'):
            prompt = f"""You are a precise and discerning code review assistant. Your task is to carefully analyze a code snippet and determine if it violates any of the *potential* bad practices listed below. These rules were identified as potentially relevant through a semantic search, but they may not all be applicable.

**Potential Bad Practices to Evaluate:**
{bad_practices_text}

**Good Practices to Follow (for context, not for flagging issues):**
{good_practices_text}

**Code to Review (with line numbers for your reference):**
```
{numbered_code_chunk}
```

**CRITICAL:** When reporting issues, use the line numbers shown in the code above (1-{len(code_chunk.splitlines())}). Do NOT try to calculate or guess other line numbers.

**IMPORTANT - SELECT * GUIDELINES:**
- DO NOT flag "SELECT *" as an issue when it's used in:
  * CREATE VIEW or CREATE TEMP VIEW statements (data loading/transformation)
  * SELECT * FROM (subquery) where the subquery explicitly lists specific columns
  * Data pipeline operations, ETL processes, or data movement between tables
  * Any context where the columns are already well-defined in an inner query
- ONLY flag "SELECT *" when it's used directly against base tables without column specification in application queries

**CRITICAL - SUGGESTION FORMATTING:**
- In your `suggestion` text, DO NOT mention specific line numbers (like "line 5", "lines 2-3", etc.)
- Instead, refer to code elements by their content (e.g., "the COALESCE expression", "the WHERE clause", "the JOIN operation")
- Focus on describing WHAT the issue is and HOW to fix it, not WHERE it appears

**Task:**
1.  **Critically evaluate** the 'Code to Review' against each of the 'Potential Bad Practices'.
2.  If you find a genuine violation, create a JSON object with the issue details. **Provide concise, actionable suggestions.**
3.  **Crucially, if the code does NOT violate any of the listed bad practices, you MUST return an empty list of issues.**
4.  Your response MUST be a single, valid JSON object. If no violations are found, return this exact JSON object: `{{"issues_found": 0, "issues": []}}`
5.  Each issue object MUST contain **only** these four keys: `line_number` (use the numbers shown in the code above), `severity`, `rule_id`, and `suggestion`. **Do not add any other keys.**

JSON Response:"""
        else:
            temperature = 0.75
            prompt = f"""You are a highly intelligent SQL code review assistant. Your primary method of finding issues (rule-based retrieval) found no relevant rules for the following code. Therefore, you must now rely entirely on your own extensive knowledge of SQL best practices to conduct a thorough review. The SQL code is written by skilled developers, so focus on advanced techniques and suggestions rather than basic tips.

**Code to Review (with line numbers for your reference):**
```
{numbered_code_chunk}
```

**CRITICAL:** When reporting issues, use the line numbers shown in the code above (1-{len(code_chunk.splitlines())}). Do NOT try to calculate or guess other line numbers.

**IMPORTANT - SELECT * GUIDELINES:**
- DO NOT flag "SELECT *" as an issue when it's used in:
  * CREATE VIEW or CREATE TEMP VIEW statements (data loading/transformation)
  * SELECT * FROM (subquery) where the subquery explicitly lists specific columns
  * Data pipeline operations, ETL processes, or data movement between tables
  * Any context where the columns are already well-defined in an inner query
- ONLY flag "SELECT *" when it's used directly against base tables without column specification in application queries

**CRITICAL - SUGGESTION FORMATTING:**
- In your `suggestion` text, DO NOT mention specific line numbers (like "line 5", "lines 2-3", etc.)
- Instead, refer to code elements by their content (e.g., "the COALESCE expression", "the WHERE clause", "the JOIN operation")
- Focus on describing WHAT the issue is and HOW to fix it, not WHERE it appears.
- AGAIN, NO LINE NUMBERS IN SUGGESTIONS. 

**Task:**
1.  **Analyze the code creatively and critically.** Look for anti-patterns, performance bottlenecks (like correlated subqueries), or security risks that may not be in a standard rulebook.
2.  **Be concise and group related feedback.** If multiple suggestions apply to the same issue, combine them into a single, comprehensive suggestion. Aim to provide a maximum of three distinct, high-impact suggestions for the code chunk.
3.  If you identify any issues, create a JSON object describing them. Your response MUST be a single, valid JSON object.
4.  For each issue, provide **only** these three keys: `line_number` (use the numbers shown in the code above), `severity` (use "AI Generated Suggestion"), and `suggestion`. **Do not include a `rule_id` or any other keys.**
5.  If you find no issues, you MUST return this exact JSON object: `{{"issues_found": 0, "issues": []}}`

**Example of a valid response:**
```json
{{
  "issues_found": 1,
  "issues": [
    {{
      "line_number": 5,
      "severity": "AI Generated Suggestion",
      "suggestion": "Consider replacing the correlated subquery with an INNER JOIN for potentially better performance, as it can leverage hash joins more effectively."
    }}
  ]
}}
```

JSON Response:"""

    # Call the Databricks LLM
    review_text = call_databricks_llm(prompt, temperature)
    
    if review_text:
        try:
            # Find the JSON object within the response text
            json_start = review_text.find('{')
            json_end = review_text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = review_text[json_start:json_end]
                return json.loads(json_str)
            else:
                print(f"Error: Could not find a valid JSON object in the response.")
                print(f"Received text: {review_text}")
                return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from response: {e}")
            print(f"Received text: {review_text}")
            return None
    else:
        print("No response received from Databricks LLM")
        return None
