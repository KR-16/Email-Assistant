import openai
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_categorizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class EmailCategorizer:
    """
    Handles email categorization using ChatGPT.
    """
    def __init__(self):
        """Initialize the categorizer."""
        self.categories = [
            'Application',
            'Interview',
            'Offer',
            'Rejection',
            'Other'
        ]

    def categorize_email(self, email_data):
        """
        Categorize an email using ChatGPT.
        
        Args:
            email_data (dict): Dictionary containing email data
                {
                    'subject': str,
                    'sender': str,
                    'body': str,
                    'snippet': str
                }
            
        Returns:
            str: Category name
        """
        try:
            # Construct prompt for ChatGPT
            prompt = f"""Read the following email and categorize it into one of these categories:
            - Application: If the email is about applying for a job or submitting a resume
            - Interview: If the email is about scheduling, confirming, or following up on an interview
            - Offer: If the email contains a job offer or discussion of employment terms
            - Rejection: If the email communicates that the candidate is not selected or rejected
            - Other: If the email doesn't clearly fit into any of the above categories

            Email Subject: {email_data['subject']}
            From: {email_data['sender']}
            Content: {email_data['body']}

            Respond with ONLY the category name (Application, Interview, Offer, Rejection, or Other).
            """

            # Call ChatGPT API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email categorization assistant. Respond with only the category name."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistent categorization
                max_tokens=10     # Limit response length
            )

            # Extract and clean category
            category = response.choices[0].message.content.strip()
            
            # Validate category
            if category not in self.categories:
                logger.warning(f"Invalid category returned: {category}. Defaulting to 'Other'")
                category = 'Other'

            logger.info(f"Categorized email '{email_data['subject']}' as {category}")
            return category

        except Exception as e:
            logger.error(f"Error categorizing email: {str(e)}")
            return 'Other'

    def batch_categorize(self, email_list):
        """
        Categorize multiple emails in batch.
        
        Args:
            email_list (list): List of email data dictionaries
            
        Returns:
            dict: Categories for each email
        """
        results = {}
        for email_data in email_list:
            category = self.categorize_email(email_data)
            results[email_data['id']] = category
        return results

if __name__ == "__main__":
    # Example usage
    categorizer = EmailCategorizer()
    
    # Test email
    test_email = {
        'id': 'test123',
        'subject': 'Interview Invitation',
        'sender': 'hr@company.com',
        'body': 'We would like to invite you for an interview...',
        'snippet': 'We would like to invite you...'
    }
    
    category = categorizer.categorize_email(test_email)
    print(f"Email categorized as: {category}") 