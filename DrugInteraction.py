import os
import groq
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

class DrugInteractionChecker:
    def __init__(self):
        """Initialize the drug interaction checker with a basic database."""
        # Sample database of known drug interactions
        self._interaction_db = {
            ('aspirin', 'warfarin'): {
                'severity': 'High',
                'effect': 'Increased risk of bleeding',
                'recommendation': 'Avoid combination'
            },
            ('ibuprofen', 'aspirin'): {
                'severity': 'Moderate',
                'effect': 'Decreased effectiveness of aspirin',
                'recommendation': 'Space doses apart'
            },
            ('omeprazole', 'clopidogrel'): {
                'severity': 'High',
                'effect': 'Reduced effectiveness of clopidogrel',
                'recommendation': 'Consider alternative medications'
            },
            ('simvastatin', 'erythromycin'): {
                'severity': 'High',
                'effect': 'Increased risk of muscle damage',
                'recommendation': 'Avoid combination'
            }
        }

    def _normalize_drug_name(self, drug: str) -> str:
        """Normalize drug name for consistent comparison."""
        return drug.lower().strip()

    def _get_interaction_key(self, drug1: str, drug2: str) -> Tuple[str, str]:
        """Create a sorted tuple of drug names for consistent dictionary lookup."""
        drugs = sorted([self._normalize_drug_name(drug1), self._normalize_drug_name(drug2)])
        return (drugs[0], drugs[1])

    def check_interaction(self, drug1: str, drug2: str) -> Optional[Dict]:
        """
        Check for known interactions between two drugs.
        Returns interaction details if found, None otherwise.
        """
        if not drug1 or not drug2:
            raise ValueError("Both drug names must be provided")

        interaction_key = self._get_interaction_key(drug1, drug2)
        return self._interaction_db.get(interaction_key)

    def get_all_known_drugs(self) -> List[str]:
        """Return a list of all drugs in the database."""
        drugs = set()
        for drug_pair in self._interaction_db.keys():
            drugs.update(drug_pair)
        return sorted(list(drugs))

def setup_groq_client() -> Optional[groq.Client]:
    """Set up and return Groq client with API key."""
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("\nError: GROQ_API_KEY not found in environment variables")
        return None
    return groq.Client(api_key=api_key)

def get_ai_drug_interaction(drug1: str, drug2: str) -> Optional[str]:
    """Query Groq API for additional drug interaction information with structured output."""
    client = setup_groq_client()
    if not client:
        return None

    try:
        system_prompt = """You are a pharmaceutical expert providing structured information about drug interactions. 
        Format your response in clear, well-organized sections with markdown formatting. For each interaction, include:
        
        ## Severity Level
        - High/Moderate/Low
        
        ## Interaction Type
        - Pharmacodynamic/Pharmacokinetic/Both
        
        ## Mechanism
        - Brief explanation of how the drugs interact
        
        ## Potential Effects
        - Bullet points of possible effects
        
        ## Recommendations
        - Specific advice for healthcare providers
        - Alternative medications if applicable
        - Monitoring parameters if needed
        
        ## Patient Counseling Points
        - What patients should know
        - When to seek medical attention
        
        ## References
        - Any relevant guidelines or studies
        
        Always include disclaimers about consulting healthcare providers.
        """
        
        user_prompt = f"""Please provide a detailed analysis of potential interactions between {drug1} and {drug2}.
        Include specific details about severity, mechanism, effects, and clinical recommendations.
        Format your response in clear, well-organized sections with markdown formatting."""
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=1000,  # Increased for more detailed responses
        )
        
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Error during AI analysis: {str(e)}")
        return None

def main():
    checker = DrugInteractionChecker()
    
    print("Welcome to the Drug Interaction Checker!")
    print("\nKnown drugs in database:", ", ".join(checker.get_all_known_drugs()))
    
    try:
        print("\nEnter the names of two medications to check for interactions.")
        drug1 = input("First medication: ").strip()
        drug2 = input("Second medication: ").strip()

        if not drug1 or not drug2:
            print("Error: Both medication names are required.")
            return

        print("\nChecking interactions...")
        
        # Check local database
        interaction = checker.check_interaction(drug1, drug2)
        if interaction:
            print("\nInteraction found in database:")
            print(f"Severity: {interaction['severity']}")
            print(f"Effect: {interaction['effect']}")
            print(f"Recommendation: {interaction['recommendation']}")
        else:
            print("\nNo known interactions found in local database.")

        # Get AI analysis
        print("\nGetting additional information from AI analysis...")
        ai_info = get_ai_drug_interaction(drug1, drug2)
        
        if ai_info:
            print("\nAI Analysis:")
            print(ai_info)
        
        print("\nDisclaimer: This information is for reference only. Always consult your healthcare provider or pharmacist about potential drug interactions.")

    except ValueError as e:
        print(f"\nError: {str(e)}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()
