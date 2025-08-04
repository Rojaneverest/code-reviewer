from openai import OpenAI
from config import LM_STUDIO_CONFIG

def interactive_chat():
    """Provides an interactive terminal session to chat with a model via LM Studio."""
    print("Connecting to LM Studio... Please ensure the server is running.")
    
    try:
        client = OpenAI(base_url=LM_STUDIO_CONFIG['api_base'], api_key=LM_STUDIO_CONFIG['api_key'])
        print("Connected successfully. Type 'exit' or 'quit' to end the session.")
    except Exception as e:
        print(f"Error connecting to LM Studio: {e}")
        return

    while True:
        prompt = input("\nEnter your prompt > ")
        if prompt.lower() in ['exit', 'quit']:
            print("Exiting chat.")
            break

        if not prompt:
            continue

        try:
            completion = client.chat.completions.create(
                model="llama-3.2-3b-instruct",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            response = completion.choices[0].message.content
            print("\nModel Response:")
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    interactive_chat()
