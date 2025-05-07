from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import pickle
from typing import List, Dict, Optional
import sys
import imaplib
import smtplib
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import (
    GMAIL_CREDENTIALS_FILE,
    GMAIL_TOKEN_FILE,
    GMAIL_SCOPES,
    EMAIL_LABELS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GmailClient:
    def __init__(self, email: str, password: str):
        """
        Initialize Gmail client with email and password.
        
        Args:
            email (str): Gmail address
            password (str): Gmail password or app password
        """
        self.email = email
        # Clean the password of any non-ASCII characters
        self.password = ''.join(char for char in password if ord(char) < 128)
        self.imap_server = "imap.gmail.com"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Test authentication before proceeding
        self._test_authentication()
        
        # Create labels if they don't exist
        self._create_labels()
    
    def _test_authentication(self) -> None:
        """Test Gmail authentication and provide helpful error messages."""
        try:
            # Test IMAP connection
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            mail.logout()
            
            # Test SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.quit()
            
            logger.info(f"Successfully authenticated Gmail account: {self.email}")
        
        except imaplib.IMAP4.error as e:
            error_msg = str(e)
            if "Application-specific password required" in error_msg:
                raise ValueError(
                    f"Account {self.email} requires an App Password. "
                    "Please generate one at: https://support.google.com/accounts/answer/185833"
                )
            elif "Invalid credentials" in error_msg:
                raise ValueError(
                    f"Invalid credentials for account {self.email}. "
                    "Please check the password in the Excel file."
                )
            else:
                raise ValueError(f"Gmail authentication failed for {self.email}: {error_msg}")
        
        except Exception as e:
            raise ValueError(f"Failed to authenticate Gmail account {self.email}: {str(e)}")
    
    def _create_labels(self) -> None:
        """Create Gmail labels if they don't exist."""
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            
            # Create labels
            labels = ['Application', 'Interview', 'Offer', 'Rejection', 'Other']
            for label in labels:
                try:
                    mail.create(label)
                except imaplib.IMAP4.error as e:
                    if "already exists" not in str(e):
                        raise
            
            mail.logout()
            logger.info(f"Successfully created Gmail labels for {self.email}")
        
        except Exception as e:
            logger.error(f"Error creating Gmail labels: {str(e)}")
            raise
    
    def get_today_emails(self) -> List[Dict]:
        """
        Get all emails received today.
        
        Returns:
            List[Dict]: List of email dictionaries containing id, subject, sender, date, and body
        """
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            
            # Select inbox
            mail.select('inbox')
            
            # Search for today's emails
            date = datetime.now().strftime("%d-%b-%Y")
            _, messages = mail.search(None, f'(SINCE "{date}")')
            
            emails = []
            for num in messages[0].split():
                _, msg = mail.fetch(num, '(RFC822)')
                email_body = msg[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Get email details
                email_id = num.decode()
                subject = email_message['subject']
                sender = email_message['from']
                date = email_message['date']
                
                # Get email body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = email_message.get_payload(decode=True).decode()
                
                emails.append({
                    'id': email_id,
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body
                })
            
            mail.logout()
            logger.info(f"Successfully fetched {len(emails)} emails for {self.email}")
            return emails
        
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            raise
    
    def apply_label(self, email_id: str, label: str) -> None:
        """
        Apply a label to an email.
        
        Args:
            email_id (str): Gmail message ID
            label (str): Label to apply
        """
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            
            # Select inbox
            mail.select('inbox')
            
            # Apply label
            mail.store(email_id, '+X-GM-LABELS', label)
            
            mail.logout()
            logger.info(f"Successfully applied label {label} to email {email_id}")
        
        except Exception as e:
            logger.error(f"Error applying label: {str(e)}")
            raise
    
    def create_draft(self, to: str, subject: str, body: str) -> None:
        """
        Create a draft email.
        
        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body
        """
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            
            # Create draft
            server.sendmail(self.email, to, message.as_string())
            
            server.quit()
            logger.info(f"Successfully created draft email to {to}")
        
        except Exception as e:
            logger.error(f"Error creating draft: {str(e)}")
            raise 