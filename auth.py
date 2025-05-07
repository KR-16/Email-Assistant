"""
Handles Authentication for Google APIs.
This module provides functions to authenticate and authorize access to Google APIs using OAuth 2.0.
"""

from datetime import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes for the Google APIs you want to access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.modify',    # Modify emails (labels)
    'https://www.googleapis.com/auth/gmail.send'       # Send emails
]

class GmailConnector:
    """
    Handles all Interactions with Gmail API
    Provides method to authenticate, fetch emails, managae and labels
    """

    def __init(self):
        """
        Initialize Gmail connector with empty credentials and service
        """

        self.credential = None
        self.service = None

    def authenticate(self):

        """
        Authenticate with Gmail using OAuth 2.0
        Uses Stored token if available, otherwise creates OAuth
        """
        # Load the credentials if they exists
        if os.path.exists("token.json"):
            self.credential = Credentials.from_authorized_user_file("token.json", SCOPES) 

        # If there are no (valid) credentials available, let the user log in.
        if not self.credential or not self.credential.valid:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            self.credential = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json","w") as token:
                token.write(self.credential.to_json())
        # Build the Gmail Service
        self.service= build("gmail", "v1", credentials = self.credential)
    
    def get_today_emails(self):
        """
        Fetch all the emails received today
        """
        """
        Returns:
        List: List of email messages objects
        """

        # Format today's date from Gmail query
        today = datetime.now().strftime("%Y/%m/%d")
        query = f"after:{today}"

        try:
            "Fetch messages from Gmail"
            results = self.service.users().messages().list(
                userId = "me",
                q = query
            ).execute()
        
            messages = results.get("messages", [])
            return messages
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            return []
        
    def get_email_Content(self, messaege_id):
        """
        Get the content of a specific Gmail

        Args:
            Message_id (str): Gmail Message ID
        
        Returns:
            str: Email body content
        """

if __name__ == "__main__":
    credential = ()
    print("Authentication successfull! Token saved in token.json")


