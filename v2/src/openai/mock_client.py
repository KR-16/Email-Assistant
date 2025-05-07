import logging
from typing import Dict, Optional
import sys
import os
from datetime import datetime
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import EMAIL_LABELS

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

class MockOpenAIClient:
    def __init__(self):
        self.model = "mock-gpt-4"
        
        # Sample responses for testing
        self.sample_responses = {
            EMAIL_LABELS['INTERVIEW']: """
Dear [Sender],

Thank you for inviting me to interview for the [Position] role. I am very interested in the opportunity and would be happy to schedule an interview.

I am available for a 30-minute call at your convenience. Please let me know what time works best for you.

Best regards,
[Your Name]
""",
            EMAIL_LABELS['OFFER']: """
Dear [Sender],

Thank you for extending the offer for the [Position] role. I am very excited about this opportunity and would like to discuss the details further.

Could you please provide more information about the compensation package and benefits? I would also appreciate knowing the expected start date.

Best regards,
[Your Name]
""",
            EMAIL_LABELS['REJECTION']: """
Dear [Sender],

Thank you for considering my application for the [Position] role. While I am disappointed to hear that I was not selected for this position, I appreciate the opportunity to have been considered.

I would be grateful if you could provide any feedback on my application or interview performance. This would help me improve for future opportunities.

Best regards,
[Your Name]
"""
        }

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

    # def categorize_email(self, email_content: str) -> str:
    #     """
    #     Mock categorization of email content.
        
    #     Args:
    #         email_content (str): The content of the email to categorize
            
    #     Returns:
    #         str: Category label (Application, Interview, Offer, Rejection, Other)
    #     """
    #     try:
    #         # Clean and prepare email content
    #         email_content = email_content.strip()
    #         if not email_content:
    #             logger.warning("Empty email content received, defaulting to 'Other'")
    #             return EMAIL_LABELS['OTHER']

    #         # Simple keyword-based categorization for testing
    #         email_content_lower = email_content.lower()
            
    #         if any(word in email_content_lower for word in ['interview', 'schedule', 'meeting']):
    #             category = EMAIL_LABELS['INTERVIEW']
    #         elif any(word in email_content_lower for word in ['offer', 'congratulations', 'welcome']):
    #             category = EMAIL_LABELS['OFFER']
    #         elif any(word in email_content_lower for word in ['reject', 'unfortunately', 'regret']):
    #             category = EMAIL_LABELS['REJECTION']
    #         elif any(word in email_content_lower for word in ['apply', 'application', 'resume']):
    #             category = EMAIL_LABELS['APPLICATION']
    #         else:
    #             category = EMAIL_LABELS['OTHER']
            
    #         # Log the AI interaction
    #         self._log_ai_interaction(
    #             operation="Email Categorization",
    #             input_data=email_content,
    #             output=f"Category: {category}\nMock Response: {category}"
    #         )
            
    #         logger.info(f"Successfully categorized email as: {category}")
    #         return category
    #     except Exception as e:
    #         error_msg = str(e)
    #         logger.error(f"Failed to categorize email: {error_msg}")
    #         # Log the error
    #         self._log_ai_interaction(
    #             operation="Email Categorization",
    #             input_data=email_content,
    #             output="Failed",
    #             error=error_msg
    #         )
    #         return EMAIL_LABELS['OTHER']

    def categorize_email(self, email_content: str) -> str:
        """
        Enhanced keyword-based email categorization with better matching logic.
        
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

            # Convert to lowercase once
            email_content_lower = email_content.lower()
            
            # Define keyword patterns with priority order (most specific first)
            patterns = [
                # Offer patterns (highest priority)
                (EMAIL_LABELS['OFFER'], [
                    'offer letter',
                    'pleased to offer',
                    'we are excited to offer',
                    'welcome to the team',
                    'compensation package',
                    'joining bonus'
                ]),
                
                # Rejection patterns
                (EMAIL_LABELS['REJECTION'], [
                    'not moving forward',
                    'not selected',
                    'unfortunately',
                    'regret to inform',
                    'other candidates',
                    'wish you the best'
                ]),
                
                # Interview patterns
                (EMAIL_LABELS['INTERVIEW'], [
                    'interview scheduled',
                    'calendar invite',
                    'zoom link',
                    'teams meeting',
                    'technical round',
                    'panel interview',
                    'hirevue',
                    'schedule a call'
                ]),
                
                # Application patterns
                (EMAIL_LABELS['APPLICATION'], [
                    'application submitted',
                    'attached my resume',
                    'applied for position',
                    'job application',
                    'reference number',
                    'application status'
                ])
            ]
            
            # Check patterns in priority order
            for category, keywords in patterns:
                if any(keyword in email_content_lower for keyword in keywords):
                    logger.info(f"Categorized email as {category} based on keywords")
                    return category
            
            # Special case: Check for false positives in rejections
            if 'interview' in email_content_lower and any(word in email_content_lower for word in ['not', 'unfortunately']):
                logger.info("Found interview reference in rejection email")
                return EMAIL_LABELS['REJECTION']
                
            # Default to Other if no matches found
            logger.info("No matching keywords found, defaulting to 'Other'")
            return EMAIL_LABELS['OTHER']
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to categorize email: {error_msg}")
            self._log_ai_interaction(
                operation="Email Categorization",
                input_data=email_content,
                output="Failed",
                error=error_msg
            )
            return EMAIL_LABELS['OTHER']

    def generate_response(self, email_content: str, category: str) -> Optional[str]:
        """
        Generate a mock response based on the email category.
        
        Args:
            email_content (str): The content of the email
            category (str): The category of the email
            
        Returns:
            Optional[str]: Generated response text or None if no response needed
        """
        try:
            if category == EMAIL_LABELS['OTHER']:
                return None

            # Get sample response for the category
            if category in self.sample_responses:
                generated_response = self.sample_responses[category]
            else:
                return None
            
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