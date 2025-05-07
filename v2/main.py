import logging
from datetime import datetime
import sys
import os
from typing import Dict, List

from src.excel.client import ExcelClient
from src.gmail.client import GmailClient
from src.openai.client import OpenAIClient
from config.config import EMAIL_LABELS, EXCEL_FILE_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EmailAssistant:
    def __init__(self):
        self.excel_client = ExcelClient(EXCEL_FILE_PATH)
        self.openai_client = OpenAIClient()
        self.gmail_clients = {}  # Dictionary to store Gmail clients for each candidate

    def get_gmail_client(self, candidate: Dict) -> GmailClient:
        """
        Get or create a Gmail client for a candidate.
        
        Args:
            candidate (Dict): Candidate information including email and password
            
        Returns:
            GmailClient: Authenticated Gmail client for the candidate
        """
        if candidate['Email'] not in self.gmail_clients:
            self.gmail_clients[candidate['Email']] = GmailClient(
                email=candidate['Email'],
                password=candidate['Password']
            )
        return self.gmail_clients[candidate['Email']]

    def process_candidate_emails(self, candidate: Dict) -> None:
        """
        Process emails for a single candidate.
        
        Args:
            candidate (Dict): Candidate information from Excel
        """
        try:
            # Get Gmail client for this candidate
            gmail_client = self.get_gmail_client(candidate)
            
            # Get today's emails
            emails = gmail_client.get_today_emails()
            
            # Process each email
            for email in emails:
                # Check if email already processed
                if self.excel_client.email_records_df[
                    self.excel_client.email_records_df['GmailMessageId'] == email['id']
                ].empty:
                    # Categorize email
                    category = self.openai_client.categorize_email(email['body'])
                    
                    # Apply Gmail label
                    gmail_client.apply_label(email['id'], category)
                    
                    # Generate response if needed
                    response = self.openai_client.generate_response(email['body'], category)
                    
                    # Store email record
                    email_data = {
                        'id': email['id'],
                        'subject': email['subject'],
                        'sender': email['sender'],
                        'category': category,
                        'received_at': datetime.strptime(email['date'], '%a, %d %b %Y %H:%M:%S %z'),
                        'response': response
                    }
                    self.excel_client.add_email_record(candidate['Id'], email_data)
                    
                    # Create draft response if generated
                    if response:
                        gmail_client.create_draft(
                            to=email['sender'],
                            subject=f"Re: {email['subject']}",
                            body=response
                        )
                    
                    logger.info(f"Successfully processed email {email['id']} for candidate {candidate['Email']}")
                else:
                    logger.info(f"Email {email['id']} already processed")
        
        except Exception as e:
            logger.error(f"Error processing emails for candidate {candidate['Email']}: {str(e)}")

    def run(self) -> None:
        """Main execution method."""
        try:
            # Fetch candidates from Excel
            candidates = self.excel_client.get_candidates()
            logger.info(f"Fetched {len(candidates)} candidates from Excel")
            
            # Process emails for each candidate
            for candidate in candidates:
                logger.info(f"Processing emails for candidate: {candidate['Email']}")
                self.process_candidate_emails(candidate)
            
            logger.info("Email processing completed successfully")
        
        except Exception as e:
            logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    assistant = EmailAssistant()
    assistant.run() 