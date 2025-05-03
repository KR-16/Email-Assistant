"""
Handles Authentication for Google APIs.
This module provides functions to authenticate and authorize access to Google APIs using OAuth 2.0.
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes for the Google APIs you want to access
SCOPES =[
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/tasks"
]

def get_authenticated_services():
    credential = None
    # Load the credentials if they exists
    if os.path.exists("token.json"):
        credential = Credentials.from_authorized_user_file("token.json", SCOPES) 

    # If there are no (valid) credentials available, let the user log in.
    if not credential or not credential.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        credential = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json","w") as token:
            token.write(credential.to_json())
    
    return credential

if __name__ == "__main__":
    credential = get_authenticated_services()
    print("Authentication successfull! Token saved in token.json")


