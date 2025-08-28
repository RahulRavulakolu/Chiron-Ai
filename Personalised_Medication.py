import os
import groq
import time
from typing import Optional, List, Dict
from dotenv import load_dotenv
from DrugInteraction import DrugInteractionChecker

def setup_groq_client() -> Optional[groq.Client]:
    """Set up and return Groq client with API key."""
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("\nError: GROQ_API_KEY not found in environment variables")
        return None
    return groq.Client(api_key=api_key)

def get_followup_question(conversation_history: List[Dict[str, str]]) -> Optional[str]:
    """Queries Groq API to generate a follow-up question based on conversation history."""
    client = setup_groq_client()
    if not client:
        return None
    
    system_prompt = """You are a medical healthcare assistant chatbot conducting a detailed assessment. 
    Your goal is to understand the patient's condition thoroughly by asking specific, relevant follow-up questions.
    
    Guidelines:
    - Ask one question at a time, targeting the most important missing information
    - Focus on symptoms, duration, severity, triggers, relieving factors, and medical history
    - Prioritize questions based on potential urgency and diagnostic value
    - Ask about medication history and allergies when relevant
    - If you have enough information to provide a preliminary assessment, indicate this with [ASSESSMENT_READY]
    """
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",  # Using a more reliable model
            temperature=0.4,
            max_tokens=150,
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        print(f"Error during API call: {str(e)}")
        return None

def get_health_assessment(conversation_history: List[Dict[str, str]]) -> Optional[str]:
    """Queries Groq API to analyze symptoms and provide a comprehensive health assessment."""
    client = setup_groq_client()
    if not client:
        return None
    
    system_prompt = """You are a medical healthcare assistant providing a thorough assessment based on the patient conversation.
    
    Provide your response in the following structured format:
    
    1. SUMMARY OF SYMPTOMS: Briefly recap the main symptoms and relevant information
    
    2. POSSIBLE CAUSES: List 2-3 potential conditions that could explain these symptoms, from most to least likely
    
    3. RECOMMENDATIONS: 
       - Provide specific self-care measures if appropriate
       - Suggest when to seek professional medical attention (urgent vs. non-urgent)
       - Recommend relevant lifestyle modifications if applicable
    
    4. IMPORTANT DISCLAIMER: Include a clear disclaimer about the limitations of this assessment
    
    Be specific, practical, and compassionate in your response while maintaining medical accuracy.
    """
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",  # Using a more reliable model
            temperature=0.3,
            max_tokens=800,
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        print(f"Error during API call: {str(e)}")
        return None

def get_personalized_medication(condition: str, patient_allergies: List[str] = None, current_medications: List[str] = None) -> Optional[Dict[str, any]]:
    """
    Get personalized medication recommendations based on condition and patient factors.
    Returns a dictionary with 'recommendations' and 'recommended_medications' keys.
    """
    print("\n=== Starting get_personalized_medication ===")
    print(f"Condition: {condition}")
    print(f"Allergies: {patient_allergies}")
    print(f"Current Medications: {current_medications}")
    
    try:
        client = setup_groq_client()
        if not client:
            raise Exception("Failed to initialize Groq client")

        if not condition or not condition.strip():
            raise ValueError("No medical condition provided")

        # Convert None to empty lists for safety
        patient_allergies = patient_allergies or []
        current_medications = current_medications or []

        allergies_text = f"Patient has allergies to: {', '.join(patient_allergies)}" if patient_allergies else "No known allergies"
        medications_text = f"Patient is currently taking: {', '.join(current_medications)}" if current_medications else "No current medications"
        
        print(f"Allergies text: {allergies_text}")
        print(f"Medications text: {medications_text}")

        # More structured prompt for better consistency
        user_prompt = f"""
        You are a medical professional providing medication recommendations.
        
        PATIENT INFORMATION:
        - Condition: {condition}
        - {allergies_text}
        - {medications_text}
        
        Please provide detailed medication recommendations following this exact structure:
        
        RECOMMENDED MEDICATIONS:
        - [Medication Name 1]: Brief description and typical usage
        - [Medication Name 2]: Brief description and typical usage
        
        USAGE GUIDELINES:
        - Specific instructions for each medication
        
        PRECAUTIONS:
        - Important warnings and considerations
        
        IMPORTANT: Always include disclaimers about consulting healthcare providers.
        """
        
        print("\n=== Sending request to Groq API ===")
        print(f"Model: llama3-70b-8192")
        print(f"Prompt length: {len(user_prompt)} characters")
        
        # Make the API call with error handling
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical AI assistant specializing in personalized medication recommendations. Provide clear, structured, and professional advice."
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=1500,  # Increased token limit for more detailed responses
        )
        
        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty or invalid response from API")
        
        # Extract the response content
        response_text = response.choices[0].message.content
        
        print("\n=== Received response from API ===")
        print(f"Response length: {len(response_text)} characters")
        print("--- Start of response ---")
        print(response_text[:500] + ("..." if len(response_text) > 500 else ""))
        print("--- End of response ---")
        
        # Extract medication names for interaction checking
        recommended_meds = []
        in_meds_section = False
        for line in response_text.split('\n'):
            line = line.strip()
            if 'RECOMMENDED MEDICATIONS:' in line.upper():
                in_meds_section = True
                continue
            if in_meds_section and line.startswith('-'):
                # Extract medication name (text between - and :)
                med_name = line.split(':')[0].replace('-', '').strip()
                if med_name and len(med_name) < 50:  # Basic validation
                    recommended_meds.append(med_name)
            elif line == '':  # Empty line might indicate end of section
                in_meds_section = False
        
        print(f"\nExtracted recommended medications: {recommended_meds}")
        
        return {
            'recommendations': response_text,
            'recommended_medications': recommended_meds
        }
        
    except Exception as e:
        error_msg = f"Error in get_personalized_medication: {str(e)}"
        print(f"\n!!! {error_msg}")
        import traceback
        traceback.print_exc()
        raise Exception(error_msg) from e

    except Exception as e:
        print(f"Error during API call: {str(e)}")
        return None

def check_medication_safety(recommended_meds: List[str], current_meds: List[str]) -> Dict[str, List[Dict]]:
    """
    Check safety of recommended medications against current medications.
    """
    checker = DrugInteractionChecker()
    interactions = {}
    
    for new_med in recommended_meds:
        med_interactions = []
        for current_med in current_meds:
            interaction = checker.check_interaction(new_med, current_med)
            if interaction:
                med_interactions.append({
                    'with_drug': current_med,
                    **interaction
                })
        if med_interactions:
            interactions[new_med] = med_interactions
    
    return interactions

def display_typing_effect(text: str, delay: float = 0.03):
    """Display text with a typing effect for a more natural interaction."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def main():
    """Main function to run the healthcare chatbot."""
    print("\n" + "="*80)
    print("🩺 PERSONALIZED HEALTHCARE ASSISTANT 🩺".center(80))
    print("="*80)
    print("\nPlease describe your symptoms and health concerns.")
    print("I'll ask follow-up questions to better understand your situation.")
    print("Type 'exit' at any time to end the conversation.\n")
    
    # Initialize conversation history
    conversation_history = []
    
    try:
        # Get initial symptoms
        initial_input = input("How can I help you today? ")
        if not initial_input.strip() or initial_input.lower() == 'exit':
            print("Goodbye! Take care of your health.")
            return
        
        # Add initial user input to conversation history
        conversation_history.append({"role": "user", "content": initial_input})
        
        # Conversation loop
        assessment_ready = False
        question_count = 0
        max_questions = 10  # Limit number of questions to prevent endless loops
        
        while question_count < max_questions and not assessment_ready:
            # Get follow-up question
            print("\nAnalyzing your information...")
            followup_question = get_followup_question(conversation_history)
            
            if not followup_question:
                print("I'm having trouble processing your information. Let's proceed with what we have.")
                break
            
            # Check if we have enough information for assessment
            if "[ASSESSMENT_READY]" in followup_question:
                assessment_ready = True
                followup_question = followup_question.replace("[ASSESSMENT_READY]", "")
                
                if followup_question.strip():
                    # Display the final question if there is one
                    display_typing_effect(f"Assistant: {followup_question}")
                    conversation_history.append({"role": "assistant", "content": followup_question})
                    
                    user_response = input("You: ")
                    if user_response.lower() == 'exit':
                        print("Goodbye! Take care of your health.")
                        return
                    
                    conversation_history.append({"role": "user", "content": user_response})
                break
            
            # Display follow-up question with typing effect
            display_typing_effect(f"Assistant: {followup_question}")
            conversation_history.append({"role": "assistant", "content": followup_question})
            
            # Get user response
            user_response = input("You: ")
            if user_response.lower() == 'exit':
                print("Goodbye! Take care of your health.")
                return
            
            conversation_history.append({"role": "user", "content": user_response})
            question_count += 1
        
        # Generate health assessment
        print("\nThank you for providing this information.")
        print("I'm now analyzing your symptoms to generate a health assessment...")
        
        result = get_health_assessment(conversation_history)
        
        if result:
            print("\n" + "-"*80)
            print("🏥 HEALTH ASSESSMENT 🏥".center(80))
            print("-"*80 + "\n")
            display_typing_effect(result)
            print("\n" + "-"*80)
            print("IMPORTANT: This assessment is not a substitute for professional medical diagnosis.")
            print("If your symptoms are severe or persistent, please consult a healthcare provider.")
            print("-"*80)
        else:
            print("\nI apologize, but I couldn't generate a health assessment at this time.")
            print("This could be due to a technical issue or insufficient information.")
            print("Please consult a healthcare professional for medical advice.")
    
    except KeyboardInterrupt:
        print("\n\nConversation interrupted. Take care of your health!")
    except Exception as e:
        print(f"\n\nAn unexpected error occurred: {str(e)}")
        print("Please try again later or consult a healthcare professional.")

if __name__ == '__main__':
    main()