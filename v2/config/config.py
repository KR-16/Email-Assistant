import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Excel Configuration
EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'data/candidates.xlsx')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Gmail Configuration
GMAIL_CREDENTIALS_FILE = 'credentials.json'
GMAIL_TOKEN_FILE = 'token.json'
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

# Email Labels
EMAIL_LABELS = {
    'APPLICATION': 'Application',
    'INTERVIEW': 'Interview',
    'OFFER': 'Offer',
    'REJECTION': 'Rejection',
    'OTHER': 'Other'
}

# ChatGPT Prompts
CATEGORIZATION_PROMPT = """
Read the following email content and categorize it into one of the following labels:
• Application – If the email is about applying for a job or submitting a resume.
• Interview – If the email is about scheduling, confirming, or following up on an interview.
• Offer – If the email contains a job offer or discussion of employment terms.
• Rejection – If the email communicates that the candidate is not selected or rejected.
• Other – If the email doesn't clearly fit into any of the above categories.

Respond with only the label name (Application, Interview, Offer, Rejection, Other).

Email content:
{email_content}
"""

# Response Generation Prompts
INTERVIEW_RESPONSE_PROMPT = """
Based on the following interview-related email, draft a professional response email.
Maintain a professional tone and ensure all questions are addressed appropriately.

Email content:
{email_content}
"""

OFFER_RESPONSE_PROMPT = """
Based on the following job offer email, draft a professional response email.
Express gratitude and request time to review the offer details.

Email content:
{email_content}
"""

REJECTION_RESPONSE_PROMPT = """
Based on the following rejection email, draft a polite and professional response.
Express gratitude for the opportunity and maintain a positive tone.

Email content:
{email_content}
""" 