import os
import groq
from typing import Optional
from dotenv import load_dotenv

def setup_groq_client() -> Optional[groq.Client]:
    """Set up and return Groq client with API key."""
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Try to get API key from environment variables
        api_key = os.getenv('GROQ_API_KEY')
        
        # Debug information
        print("\n=== Debug Information ===")
        print(f"Current working directory: {os.getcwd()}")
        print(f".env file exists: {os.path.exists('.env')}")
        print(f"GROQ_API_KEY exists: {api_key is not None}")
        print("========================\n")
        
        if not api_key:
            print("Error: GROQ_API_KEY not found in environment variables")
            print("Please ensure you have a .env file in the project root with GROQ_API_KEY=your_api_key")
            return None
            
        # Test the API key by creating a client
        client = groq.Client(api_key=api_key)
        
        # Test the connection with a simple request
        try:
            test_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            print("Successfully connected to Groq API")
            return client
            
        except Exception as e:
            print(f"Error testing Groq API connection: {str(e)}")
            print("Please check your API key and internet connection")
            return None
            
    except Exception as e:
        print(f"Unexpected error setting up Groq client: {str(e)}")
        return None

def get_available_models():
    """Get list of available models from Groq"""
    try:
        client = setup_groq_client()
        if not client:
            return []
        # List of currently available models from Groq (as of August 2024)
        test_models = [
            "llama3-70b-8192",  # Most capable model
            "llama3-8b-8192",   # Faster but less capable
            "mixtral-8x7b-32768",  # Some users report this still works
            "gemma-7b-it"       # Alternative model
        ]
        
        available_models = []
        for model in test_models:
            try:
                client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                available_models.append(model)
            except:
                continue
                
        return available_models
    except Exception as e:
        print(f"Error checking available models: {e}")
        return []

def get_disease_from_symptoms(symptoms: str) -> Optional[str]:
    """
    Queries Groq API to analyze symptoms and return the most likely disease with a description.
    Uses the latest stable model from Groq.
    """
    try:
        client = setup_groq_client()
        if not client:
            print("Error: Failed to initialize Groq client")
            return "Error: Failed to initialize the AI service. Please check your API key and try again."

        if not symptoms or not symptoms.strip():
            print("Error: No symptoms provided")
            return "Error: Please describe your symptoms in the input field."

        print(f"Sending request to Groq API with symptoms: {symptoms[:100]}...")  # Log first 100 chars
        
        # Use the latest stable model from Groq
        model_to_use = "llama3-70b-8192"  # Most capable model as of August 2024
        print(f"Using model: {model_to_use}")
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": ("You are a medical AI assistant that identifies potential conditions based on symptoms. "
                              "Format your response with clear sections using markdown formatting. For any symptoms described, provide:\n"
                              "## Possible Conditions\n"
                              "1. **Condition Name**  \n"
                              "   *Brief description*  \n"
                              "   **When to seek help:** *Guidance*  \n"
                              "   **Self-care:** *Advice*  \n\n"
                              "2. **Condition Name**  \n"
                              "   *Brief description*  \n"
                              "   **When to seek help:** *Guidance*  \n"
                              "   **Self-care:** *Advice*  \n\n"
                              "## General Advice\n"
                              "- *General self-care recommendations*\n"
                              "- *When to see a doctor*\n\n"
                              "## Important Note\n"
                              "*This information is for educational purposes only and is not a substitute for professional medical advice. Always consult with a healthcare provider for proper diagnosis and treatment.*")
                },
                {
                    "role": "user", 
                    "content": f"Please analyze these symptoms: {symptoms}"
                }
            ],
            model=model_to_use,
            temperature=0.5,  # Balanced temperature for reliable responses
            max_tokens=1000,  # Increased token limit for detailed responses
        )
        
        if not response or not response.choices or not response.choices[0].message.content:
            print("Error: Empty or invalid response from API")
            return "Error: Received an invalid response from the AI service. Please try again."
            
        result = response.choices[0].message.content
        print(f"Received response from Groq API: {result[:200]}...")  # Log first 200 chars
        return result

    except Exception as e:
        error_msg = f"Error during symptom analysis: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg} Please check your API key and try again."

def main():
    print("Welcome to the Symptom Analyzer!")
    print("Please enter your symptoms (e.g., fever, cough, fatigue):")
    
    try:
        symptoms = input().strip()
        if not symptoms:
            print("No symptoms entered. Please try again.")
            return

        print("\nAnalyzing symptoms...")
        result = get_disease_from_symptoms(symptoms)
        
        if result:
            print("\nAnalysis Result:")
            print(result)
            print("\nDisclaimer: This is for informational purposes only. Always consult a healthcare professional for medical advice.")
        else:
            print("\nCould not analyze symptoms at this time. Please check if your API key is correct.")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()
