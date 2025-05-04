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

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

class GmailConnector:
    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self):
        """Authenticate with Gmail API."""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_today_emails(self):
        """Fetch all emails received today."""
        today = datetime.now().strftime('%Y/%m/%d')
        query = f'after:{today}'
        
        try:
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
        """Get the content of a specific email."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract email body
            if 'payload' in message:
                parts = message['payload'].get('parts', [])
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
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
        """Apply a label to an email."""
        try:
            # Get or create label
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    label_id = label['id']
                    break
            
            if not label_id:
                # Create new label
                new_label = self.service.users().labels().create(
                    userId='me',
                    body={'name': label_name}
                ).execute()
                label_id = new_label['id']
            
            # Apply label
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
        """Create a draft email."""
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            return draft
            
        except Exception as e:
            print(f"Error creating draft: {str(e)}")
            return None 