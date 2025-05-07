import openai
import logging
from typing import Dict, Optional
import sys
import os
from datetime import datetime

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a file handler for AI interactions
ai_log_dir = 'logs'
if not os.path.exists(ai_log_dir):
    os.makedirs(ai_log_dir)

ai_log_file = os.path.join(ai_log_dir, 'ai_interactions.log')
ai_handler = logging.FileHandler(ai_log_file)
ai_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
logger.addHandler(ai_handler)

class OpenAIClient:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.model = "gpt-4o-mini"  # Using the correct model name

    def _log_ai_interaction(self, operation: str, input_data: str, output: str, error: Optional[str] = None) -> None:
        """
        Log AI interaction details to a dedicated log file.
        
        Args:
            operation (str): Type of operation (categorization/response)
            input_data (str): Input data sent to AI
            output (str): Output received from AI
            error (Optional[str]): Any error that occurred
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n{'='*80}\n"
        log_entry += f"Timestamp: {timestamp}\n"
        log_entry += f"Operation: {operation}\n"
        log_entry += f"Model: {self.model}\n"
        log_entry += f"\nInput:\n{'-'*40}\n{input_data}\n"
        log_entry += f"\nOutput:\n{'-'*40}\n{output}\n"
        if error:
            log_entry += f"\nError:\n{'-'*40}\n{error}\n"
        log_entry += f"{'='*80}\n"
        
        logger.info(log_entry)

    def categorize_email(self, email_content: str) -> str:
        """
        Categorize email content using ChatGPT.
        
        Args:
            email_content (str): The content of the email to categorize
            
        Returns:
            str: Category label (Application, Interview, Offer, Rejection, Other)
        """
        try:
            # Clean and prepare email content
            email_content = email_content.strip()
            if not email_content:
                logger.warning("Empty email content received, defaulting to 'Other'")
                return EMAIL_LABELS['OTHER']

            prompt = CATEGORIZATION_PROMPT.format(email_content=email_content)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an email categorization assistant. Respond with ONLY one of these exact labels: Application, Interview, Offer, Rejection, Other."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent categorization
                max_tokens=50
            )
            
            category = response.choices[0].message.content.strip()
            logger.info(f"Raw category response: {category}")
            
            # Validate category
            if category not in EMAIL_LABELS.values():
                logger.warning(f"Invalid category returned: {category}. Defaulting to 'Other'")
                category = EMAIL_LABELS['OTHER']
            
            # Log the AI interaction
            self._log_ai_interaction(
                operation="Email Categorization",
                input_data=email_content,
                output=f"Category: {category}\nRaw Response: {response.choices[0].message.content}"
            )
            
            logger.info(f"Successfully categorized email as: {category}")
            return category
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to categorize email: {error_msg}")
            # Log the error
            self._log_ai_interaction(
                operation="Email Categorization",
                input_data=email_content,
                output="Failed",
                error=error_msg
            )
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
            
            # Log the AI interaction
            self._log_ai_interaction(
                operation=f"Response Generation ({category})",
                input_data=email_content,
                output=generated_response
            )
            
            logger.info(f"Successfully generated response for {category} email")
            return generated_response
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to generate response: {error_msg}")
            # Log the error
            self._log_ai_interaction(
                operation=f"Response Generation ({category})",
                input_data=email_content,
                output="Failed",
                error=error_msg
            )
            return None 