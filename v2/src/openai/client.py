import openai
import logging
from typing import Dict, Optional
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import (
    OPENAI_API_KEY,
    CATEGORIZATION_PROMPT,
    INTERVIEW_RESPONSE_PROMPT,
    OFFER_RESPONSE_PROMPT,
    REJECTION_RESPONSE_PROMPT,
    EMAIL_LABELS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.model = "gpt-4"  # Using GPT-4 for better accuracy

    def categorize_email(self, email_content: str) -> str:
        """
        Categorize email content using ChatGPT.
        
        Args:
            email_content (str): The content of the email to categorize
            
        Returns:
            str: Category label (Application, Interview, Offer, Rejection, Other)
        """
        try:
            prompt = CATEGORIZATION_PROMPT.format(email_content=email_content)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an email categorization assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent categorization
                max_tokens=50
            )
            
            category = response.choices[0].message.content.strip()
            
            # Validate category
            if category not in EMAIL_LABELS.values():
                logger.warning(f"Invalid category returned: {category}. Defaulting to 'Other'")
                category = EMAIL_LABELS['OTHER']
            
            logger.info(f"Successfully categorized email as: {category}")
            return category
        except Exception as e:
            logger.error(f"Failed to categorize email: {str(e)}")
            return EMAIL_LABELS['OTHER']

    def generate_response(self, email_content: str, category: str) -> Optional[str]:
        """
        Generate an appropriate response based on the email category.
        
        Args:
            email_content (str): The content of the email
            category (str): The category of the email
            
        Returns:
            Optional[str]: Generated response text or None if no response needed
        """
        try:
            if category == EMAIL_LABELS['OTHER']:
                return None

            # Select appropriate prompt based on category
            if category == EMAIL_LABELS['INTERVIEW']:
                prompt = INTERVIEW_RESPONSE_PROMPT
            elif category == EMAIL_LABELS['OFFER']:
                prompt = OFFER_RESPONSE_PROMPT
            elif category == EMAIL_LABELS['REJECTION']:
                prompt = REJECTION_RESPONSE_PROMPT
            else:
                return None

            prompt = prompt.format(email_content=email_content)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an email response assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Higher temperature for more creative responses
                max_tokens=500
            )
            
            generated_response = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated response for {category} email")
            return generated_response
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return None 