from openai import OpenAI
import sys
import os
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import LM_STUDIO_CONFIG

# Initialize the OpenAI client to connect to LM Studio
client = OpenAI(base_url=LM_STUDIO_CONFIG['api_base'], api_key=LM_STUDIO_CONFIG['api_key'])

def generate_review(code_chunk, rules, retrieval_method="Vector Search"):
    """Generates a code review in a structured JSON format by calling the LM Studio model."""
    
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

    # Dynamically construct the prompt based on the retrieval method
    if retrieval_method == "Regex Match":
        # This prompt is direct and handles multiple potential violations found by regex.
        prompt = f"""You are a precise code review assistant. A code snippet has been identified as potentially violating one or more bad practices via direct Regex Matches.

**Bad Practices Found by Regex:**
{bad_practices_text}

**Code to Review:**
```
{code_chunk}
```

**Task:**
Your task is to review the code and confirm each violation from the list of 'Bad Practices Found by Regex'.

Your response MUST be a single, valid JSON object. The JSON should contain a list of all confirmed issues. For each issue, provide **only** these four keys: `line_number` (relative to the chunk), `severity`, `rule_id`, and `suggestion`.

If you cannot confirm any of the violations, you MUST return this exact JSON object:
{{"issues_found": 0, "issues": []}}

JSON Response:"""
    else:  # Vector Search
        if rules.get('bad_practices'):
            # This prompt is cautious, asking the LLM to verify the violation first based on retrieved rules.
            prompt = f"""You are a precise and discerning code review assistant. Your task is to carefully analyze a code snippet and determine if it violates any of the *potential* bad practices listed below. These rules were identified as potentially relevant through a semantic search, but they may not all be applicable.

**Potential Bad Practices to Evaluate:**
{bad_practices_text}

**Good Practices to Follow (for context, not for flagging issues):**
{good_practices_text}

**Code to Review:**
```
{code_chunk}
```

**Task:**
1.  **Critically evaluate** the 'Code to Review' against each of the 'Potential Bad Practices'.
2.  If you find a genuine violation, create a JSON object with the issue details (line number, severity, rule ID, suggestion).
3.  **Crucially, if the code does NOT violate any of the listed bad practices, you MUST return an empty list of issues.**

Your response MUST be a single, valid JSON object. If no violations are found, return this exact JSON object:
{{"issues_found": 0, "issues": []}}

JSON Response:"""
        else:
            # This prompt is open-ended, asking the LLM to use its own knowledge when no rules are found.
            # We also increase the temperature to allow for more creative, non-deterministic responses.
            temperature = 0.75
            prompt = f"""You are a highly intelligent SQL code review assistant. Your primary method of finding issues (rule-based retrieval) found no relevant rules for the following code.

Therefore, you must now rely entirely on your own extensive knowledge of SQL best practices, performance tuning, and security to conduct a thorough review. These sql codes are written by skilled employees, hence don't include basic tips as suggestions rather go into advanced sql techniques or suggestions.   

**Code to Review:**
```
{code_chunk}
```

**Task:**
1.  **Analyze the code creatively and critically.** Look for anti-patterns, performance bottlenecks (like correlated subqueries), or security risks that may not be in a standard rulebook.
2.  If you identify any issues, create a JSON object describing them.
3.  For each issue, provide **only** these three keys: `line_number` (relative to the chunk), `severity` (use the special value "AI Generated Suggestion"), and `suggestion`.
4.  **Do not include a `rule_id`.**

Your response MUST be a single, valid JSON object. If you find no issues, you MUST return this exact JSON object:
{{"issues_found": 0, "issues": []}}

JSON Response:"""

    try:
        completion = client.chat.completions.create(
            model="", # Use a model name recognized by your LM Studio server
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature # Use the dynamically set temperature
        )
        review_text = completion.choices[0].message.content

        # Find the JSON object within the response text
        try:
            # The model might return the JSON wrapped in markdown ```json ... ```
            json_start = review_text.find('{')
            json_end = review_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = review_text[json_start:json_end]
                return json.loads(json_str)
            else:
                print(f"Error: Could not find a valid JSON object in the response.")
                return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from response: {e}")
            print(f"Received text: {review_text}")
            return None
    except Exception as e:
        print(f"Error connecting to LM Studio or parsing JSON: {e}")
        return None
