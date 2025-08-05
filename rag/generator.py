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

def call_lm_studio(prompt, temperature):
    try:
        completion = client.chat.completions.create(
            model="local-model", # Use a model name recognized by your LM Studio server
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature # Set to 0 for deterministic, structured output
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error connecting to LM Studio: {e}")
        return None

def generate_review(code_chunk, rules, temperature=0.1, max_retries=3):
    """Generates a code review, retrying on failure to parse LLM output."""
    # Prepare the rules text for the prompt
    rules_text = "\n".join([
        f"- **Rule ID {r['id']} ({r['severity']}):** {r['title']}. {r['description']} Suggestion: {r['suggestion']}"
        for r in rules
    ]) if rules else "None"

    # Construct the final prompt
    prompt = f"""You are a precise and thorough SQL code review assistant. Your task is to find violations of the following SQL best practices in the code snippet provided.

**Rules to Check:**
{rules_text}

**Code to Review:**
```
{code_chunk}
```

**Instructions:**
- Analyze the code ONLY against the 'Rules to Check'.
- If a rule is not relevant to the code, ignore it.
- Report only confirmed violations.
- Your response MUST be a single, valid JSON object.
- For each violation, provide the line number, severity, rule ID, and a concise suggestion.

If no violations are found, return this exact JSON object:
{{"issues_found": 0, "issues": []}}

JSON Response:"""

    # Retry loop for calling the language model and parsing the response
    for attempt in range(max_retries):
        try:
            # Call the language model
            response = call_lm_studio(prompt, temperature)

            # Find the start of the JSON object and extract it
            json_start = response.find('{')
            if json_start == -1:
                raise json.JSONDecodeError("No JSON object found in response", response, 0)
            
            json_response = response[json_start:]
            
            # Parse the JSON and return successfully
            review_data = json.loads(json_response)
            return review_data
        
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: Error parsing JSON. {e}")
            if attempt + 1 == max_retries:
                print(f"Final attempt failed. Raw response: {response}")
                return None # Return None after the last failed attempt

    return None # Should not be reached, but as a fallback
