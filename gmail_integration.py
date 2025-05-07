# Import required libraries
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64
from email.mime.text import MIMEText
import json
import logging
from email_categorizer import EmailCategorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmail_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define required Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.modify',    # Modify emails (labels)
    'https://www.googleapis.com/auth/gmail.send'       # Send emails
]

class GmailConnector:
    """
    Handles all interactions with Gmail API.
    Provides methods to authenticate, fetch emails, and manage labels.
    """
    def __init__(self):
        """Initialize Gmail connector with empty credentials and service."""
        self.creds = None
        self.service = None
        self.label_ids = {}  # Cache for label IDs
        self.categorizer = EmailCategorizer()

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth 2.0.
        Uses stored token if available, otherwise initiates OAuth flow.
        """
        # Check for existing token
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If no valid credentials, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Refresh expired token
                self.creds.refresh(Request())
            else:
                # Start OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=self.creds)
        # Initialize label cache
        self._initialize_label_cache()

    def _initialize_label_cache(self):
        """Initialize the cache of label IDs."""
        try:
            labels = self.service.users().labels().list(userId='me').execute()
            for label in labels.get('labels', []):
                self.label_ids[label['name']] = label['id']
        except Exception as e:
            logger.error(f"Error initializing label cache: {str(e)}")

    def get_inbox_emails(self, max_results=100):
        """
        Fetch unread emails from the main inbox.
        
        Args:
            max_results (int): Maximum number of emails to fetch
            
        Returns:
            list: List of email message objects
        """
        try:
            # Query for unread emails in inbox
            query = 'in:inbox is:unread'
            
            # Fetch messages from Gmail
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} unread emails in inbox")
            return messages
            
        except Exception as e:
            logger.error(f"Error fetching inbox emails: {str(e)}")
            return []

    def get_email_content(self, message_id):
        """
        Get the content of a specific email.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            dict: Email content including subject, body, and sender
        """
        try:
            # Fetch full message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract email headers and body
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            # Extract email body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(
                    message['payload']['body']['data']
                ).decode('utf-8')
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'body': body,
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            logger.error(f"Error getting email content: {str(e)}")
            return None

    def create_label(self, label_name):
        """
        Create a new Gmail label if it doesn't exist.
        
        Args:
            label_name (str): Name of the label to create
            
        Returns:
            str: Label ID
        """
        try:
            # Check if label already exists
            if label_name in self.label_ids:
                return self.label_ids[label_name]
            
            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            # Update cache
            self.label_ids[label_name] = created_label['id']
            logger.info(f"Created new label: {label_name}")
            return created_label['id']
            
        except Exception as e:
            logger.error(f"Error creating label: {str(e)}")
            return None

    def move_to_label(self, message_id, label_name):
        """
        Move an email to a specific label and remove it from inbox.
        
        Args:
            message_id (str): Gmail message ID
            label_name (str): Name of the label to move to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get or create label
            label_id = self.create_label(label_name)
            if not label_id:
                return False
            
            # Get INBOX label ID
            inbox_id = self.label_ids.get('INBOX')
            if not inbox_id:
                logger.error("Could not find INBOX label ID")
                return False
            
            # Modify message labels
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': [label_id],
                    'removeLabelIds': [inbox_id]
                }
            ).execute()
            
            logger.info(f"Moved email {message_id} to label {label_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving email to label: {str(e)}")
            return False

    def process_inbox(self, max_emails=100):
        """
        Process unread emails in the inbox.
        
        Args:
            max_emails (int): Maximum number of emails to process
            
        Returns:
            dict: Processing statistics
        """
        stats = {
            'processed': 0,
            'errors': 0,
            'by_category': {
                'Application': 0,
                'Interview': 0,
                'Offer': 0,
                'Rejection': 0,
                'Other': 0
            }
        }
        
        try:
            # Get unread emails from inbox
            messages = self.get_inbox_emails(max_emails)
            
            for message in messages:
                try:
                    # Get email content
                    email_data = self.get_email_content(message['id'])
                    if not email_data:
                        stats['errors'] += 1
                        continue
                    
                    # Categorize email using ChatGPT
                    category = self.categorizer.categorize_email(email_data)
                    
                    # Move email to appropriate label
                    if self.move_to_label(message['id'], category):
                        stats['processed'] += 1
                        stats['by_category'][category] += 1
                    else:
                        stats['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing email {message['id']}: {str(e)}")
                    stats['errors'] += 1
            
            logger.info(f"Processed {stats['processed']} emails with {stats['errors']} errors")
            return stats
            
        except Exception as e:
            logger.error(f"Error processing inbox: {str(e)}")
            return stats

if __name__ == "__main__":
    # Example usage
    gmail = GmailConnector()
    gmail.authenticate()
    results = gmail.process_inbox()
    print(f"Processing results: {results}") 