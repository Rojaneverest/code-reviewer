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

def generate_review(code_chunk, rules):
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

    # Construct the final prompt using the specified template
    prompt = f"""You are a precise code review assistant. Your task is to find violations of bad practices in a code snippet, while being aware of good practices.

**Bad Practices to Avoid:**
{bad_practices_text}

**Good Practices to Follow (for context, not for flagging issues):**
{good_practices_text}

**Code to Review:**
```
{code_chunk}
```

**Task:**
Compare the code ONLY against the 'Bad Practices to Avoid'. Do NOT flag 'Good Practices'. Identify all violations of the bad practices. Your response MUST be a single, valid JSON object. The JSON should contain a list of issues found. For each issue, provide the line number, severity, the ID of the rule that was violated, and a suggestion for fixing it.

If no violations are found, return this exact JSON object:
{{"issues_found": 0, "issues": []}}

JSON Response:"""

    try:
        completion = client.chat.completions.create(
            model="local-model", # Use a model name recognized by your LM Studio server
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0 # Set to 0 for deterministic, structured output
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
