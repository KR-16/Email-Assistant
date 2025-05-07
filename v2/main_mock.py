"""
Email Assistant Mock Application
==============================

This module provides a mock implementation of the email assistant that processes
emails for job candidates without using the actual OpenAI API. It's designed for
testing and development purposes.

The application:
1. Reads candidate information from an Excel file
2. Connects to each candidate's Gmail account
3. Processes emails based on specified time range
4. Categorizes emails using keyword matching
5. Generates response drafts
6. Records all actions in Excel

Author: Your Name
Date: 2024
"""

import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
from email.utils import parsedate_to_datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gmail.client import GmailClient
from src.openai.mock_client import MockOpenAIClient
from src.excel.client import ExcelClient
from config.config import (
    EXCEL_FILE_PATH,
    EMAIL_LABELS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mock_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MockEmailAssistant:
    """
    Mock implementation of the email assistant.
    
    This class provides functionality to process emails for job candidates
    using mock AI components instead of the actual OpenAI API. It's designed
    for testing and development purposes.
    
    Attributes:
        excel_client (ExcelClient): Client for Excel operations
        ai_client (MockOpenAIClient): Mock AI client for categorization and response generation
        gmail_clients (Dict): Cache of Gmail clients for each candidate
    """
    
    def __init__(self):
        """Initialize the email assistant with mock components."""
        self.excel_client = ExcelClient(EXCEL_FILE_PATH)
        self.ai_client = MockOpenAIClient()
        self.gmail_clients = {}  # Cache for Gmail clients
        logger.info("Initialized MockEmailAssistant")

    def get_gmail_client(self, candidate: Dict) -> GmailClient:
        """
        Get or create a Gmail client for a candidate.
        
        This method implements a caching mechanism to avoid creating multiple
        Gmail clients for the same candidate.
        
        Args:
            candidate (Dict): Candidate information including email and password
            
        Returns:
            GmailClient: Authenticated Gmail client for the candidate
            
        Raises:
            Exception: If Gmail client creation fails
        """
        email = candidate['Email']
        if email not in self.gmail_clients:
            try:
                self.gmail_clients[email] = GmailClient(
                    email=email,
                    password=candidate['Password']
                )
                logger.info(f"Created new Gmail client for {email}")
            except Exception as e:
                logger.error(f"Failed to create Gmail client for {email}: {str(e)}")
                raise
        return self.gmail_clients[email]

    def process_candidate_emails(self, candidate: Dict, time_range: str = 'today') -> None:
        """
        Process emails for a single candidate.
        
        This method:
        1. Gets or creates a Gmail client for the candidate
        2. Fetches emails for the specified time range
        3. Processes each unprocessed email:
           - Categorizes it using the mock AI client
           - Applies appropriate Gmail label
           - Generates a response draft
           - Records the action in Excel
        
        Args:
            candidate (Dict): Candidate information from Excel
            time_range (str): Time range to process emails for ('today', 'yesterday', or 'last_week')
            
        Note:
            - Only processes emails that haven't been processed before
            - Creates response drafts without sending them
            - Handles errors for individual emails without stopping the entire process
        """
        try:
            # Get Gmail client
            gmail_client = self.get_gmail_client(candidate)
            logger.info(f"Processing emails for {candidate['Email']}")
            
            # Get emails based on time range
            if time_range == 'today':
                emails = gmail_client.get_today_emails()
                logger.info(f"Found {len(emails)} emails from today for {candidate['Email']}")
            elif time_range == 'yesterday':
                emails = gmail_client.get_yesterday_emails()
                logger.info(f"Found {len(emails)} emails from yesterday for {candidate['Email']}")
            elif time_range == 'last_week':
                emails = gmail_client.get_last_week_emails()
                logger.info(f"Found {len(emails)} emails from the last week for {candidate['Email']}")
            else:
                raise ValueError(f"Invalid time range: {time_range}")
            
            for email in emails:
                try:
                    # Check if email already processed
                    if self.excel_client.email_records_df[
                        self.excel_client.email_records_df['GmailMessageId'] == email['id']
                    ].empty:
                        # Categorize email
                        category = self.ai_client.categorize_email(email['body'])
                        logger.info(f"Categorized email as: {category}")
                        
                        # Apply label
                        gmail_client.apply_label(email['id'], category)
                        logger.info(f"Applied label {category} to email {email['id']}")
                        
                        # Generate response if needed
                        response = self.ai_client.generate_response(email['body'], category)
                        
                        # Parse email date
                        received_at = parsedate_to_datetime(email['date'])
                        
                        # Store email record
                        email_data = {
                            'id': email['id'],
                            'subject': email['subject'],
                            'sender': email['sender'],
                            'category': category,
                            'received_at': received_at,
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
                            logger.info(f"Created draft response for email {email['id']}")
                        
                        logger.info(f"Successfully processed email {email['id']}")
                    else:
                        logger.info(f"Email {email['id']} already processed")
                
                except Exception as e:
                    logger.error(f"Error processing email {email['id']}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error processing emails for {candidate['Email']}: {str(e)}")

    def run(self, time_range: str = 'today') -> None:
        """
        Main execution method.
        
        This method:
        1. Fetches all candidates from Excel
        2. Processes emails for each candidate
        3. Handles errors for individual candidates without stopping the entire process
        
        Args:
            time_range (str): Time range to process emails for ('today', 'yesterday', or 'last_week')
            
        Note:
            - Continues processing even if one candidate fails
            - Logs all actions and errors
            - Saves all records to Excel
        """
        try:
            # Get candidates
            candidates = self.excel_client.get_candidates()
            logger.info(f"Found {len(candidates)} candidates")
            
            # Process each candidate
            for candidate in candidates:
                try:
                    logger.info(f"Processing candidate: {candidate['Email']}")
                    self.process_candidate_emails(candidate, time_range)
                except Exception as e:
                    logger.error(f"Error processing candidate {candidate['Email']}: {str(e)}")
                    continue
            
            logger.info("Email processing completed successfully")
        
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            raise

def main():
    """
    Entry point for the application.
    
    This function:
    1. Creates an instance of MockEmailAssistant
    2. Runs the email processing
    3. Handles any fatal errors
    
    Note:
        - Exits with status code 1 if a fatal error occurs
        - Logs all actions and errors
    """
    try:
        assistant = MockEmailAssistant()
        # You can change the time_range parameter to 'today', 'yesterday', or 'last_week'
        assistant.run(time_range='yesterday')
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 