# Import required libraries
import openai
import os
from dotenv import load_dotenv
from models import EmailResponse, init_db
from sqlalchemy.orm import sessionmaker

# Load environment variables and set OpenAI API key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class ChatGPTProcessor:
    """
    Handles all interactions with OpenAI's ChatGPT API.
    Provides methods for email categorization and response generation.
    """
    def __init__(self):
        """Initialize database connection for storing responses."""
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)

    def categorize_email(self, email_content):
        """
        Categorize email content using ChatGPT.
        
        Args:
            email_content (str): The content of the email to categorize
            
        Returns:
            str: Category name (Application, Interview, Offer, Rejection, Other)
        """
        try:
            # Construct prompt for ChatGPT
            prompt = f"""Read the following email content and categorize it into one of the following labels:
            - Application – If the email is about applying for a job or submitting a resume.
            - Interview – If the email is about scheduling, confirming, or following up on an interview.
            - Offer – If the email contains a job offer or discussion of employment terms.
            - Rejection – If the email communicates that the candidate is not selected or rejected.
            - Other – If the email doesn't clearly fit into any of the above categories.

            Respond with only the label name (Application, Interview, Offer, Rejection, Other).

            Email content:
            {email_content}
            """

            # Call ChatGPT API for categorization
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email categorization assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistent categorization
                max_tokens=10     # Limit response length
            )

            # Extract and clean category
            category = response.choices[0].message.content.strip()
            return category

        except Exception as e:
            print(f"Error categorizing email: {str(e)}")
            return "Other"

    def generate_response(self, email_content, category):
        """
        Generate an appropriate response based on the email category.
        
        Args:
            email_content (str): The content of the email
            category (str): The category of the email
            
        Returns:
            str: Generated response text or None if no response needed
        """
        try:
            # Skip response generation for 'Other' category
            if category == "Other":
                return None

            # Construct prompt for response generation
            prompt = f"""Based on the following email content and its category ({category}), 
            draft a professional and appropriate response email. The response should be:
            - Professional and courteous
            - Relevant to the email content
            - Appropriate for the category
            - Concise and clear

            Email content:
            {email_content}

            Please provide only the body of the response email, without any headers or signatures.
            """

            # Call ChatGPT API for response generation
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email response assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Higher temperature for more creative responses
                max_tokens=500    # Allow longer responses
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None

    def store_response(self, candidate_id, email_id, category, response_draft):
        """
        Store the generated response in the database.
        
        Args:
            candidate_id (int): ID of the candidate
            email_id (str): Gmail message ID
            category (str): Email category
            response_draft (str): Generated response text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create database session
            session = self.Session()
            
            # Create new response record
            email_response = EmailResponse(
                candidate_id=candidate_id,
                email_id=email_id,
                category=category,
                response_draft=response_draft
            )
            
            # Save to database
            session.add(email_response)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            print(f"Error storing response: {str(e)}")
            return False 