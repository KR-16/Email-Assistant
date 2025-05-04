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

    def get_today_emails(self):
        """
        Fetch all emails received today.
        
        Returns:
            list: List of email message objects
        """
        # Format today's date for Gmail query
        today = datetime.now().strftime('%Y/%m/%d')
        query = f'after:{today}'
        
        try:
            # Fetch messages from Gmail
            results = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            return messages
            
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            return []

    def get_email_content(self, message_id):
        """
        Get the content of a specific email.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            str: Email body content
        """
        try:
            # Fetch full message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract email body from message parts
            if 'payload' in message:
                parts = message['payload'].get('parts', [])
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        # Decode base64-encoded email body
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                return body
            return ''
            
        except Exception as e:
            print(f"Error getting email content: {str(e)}")
            return ''

    def apply_label(self, message_id, label_name):
        """
        Apply a label to an email.
        Creates the label if it doesn't exist.
        
        Args:
            message_id (str): Gmail message ID
            label_name (str): Name of the label to apply
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get existing labels
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            # Find existing label
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    label_id = label['id']
                    break
            
            # Create new label if not exists
            if not label_id:
                new_label = self.service.users().labels().create(
                    userId='me',
                    body={'name': label_name}
                ).execute()
                label_id = new_label['id']
            
            # Apply label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error applying label: {str(e)}")
            return False

    def create_draft(self, to, subject, body):
        """
        Create a draft email.
        
        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body content
            
        Returns:
            dict: Draft message object or None if failed
        """
        try:
            # Create MIME message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            # Encode message for Gmail API
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Create draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            return draft
            
        except Exception as e:
            print(f"Error creating draft: {str(e)}")
            return None 