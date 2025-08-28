import os
from dotenv import load_dotenv
import groq

def test_groq_connection():
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment variables")
        return False
    
    try:
        client = groq.Client(api_key=api_key)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            model="llama3-70b-8192",
            max_tokens=10
        )
        print("API connection successful!")
        print("Response:", response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"Error connecting to Groq API: {str(e)}")
        return False

if __name__ == "__main__":
    test_groq_connection()
