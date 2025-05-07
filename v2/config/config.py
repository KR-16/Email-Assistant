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
You are an expert at categorizing job-related emails. Analyze the following email content and respond with EXACTLY ONE of the following labels and NOTHING ELSE:

• Application 
  – If the email is about:
  - Submitting a job application
  - Sending a resume/CV
  - Initial job inquiry
  - Application status check
  - Application confirmation

• Interview 
  – If the email is about:
  - Interview scheduling
  - Interview confirmation
  - Interview preparation details
  - Interview feedback
  - Interview follow-up
  - Technical assessment details

• Offer 
  – If the email contains:
  - Job offer details
  - Salary/compensation discussion
  - Benefits information
  - Start date discussion
  - Offer acceptance/negotiation
  - Contract details

• Rejection 
  – If the email:
  - Declines the application
  - Indicates the candidate wasn't selected
  - Suggests applying for other positions
  - Provides feedback on the application

• Other 
  – If the email doesn't clearly fit the above categories or is about:
  - General company information
  - Networking
  - Job alerts
  - Newsletter
  - Marketing content

Respond with EXACTLY ONE of these labels and NOTHING ELSE:
- Application
- Interview
- Offer
- Rejection
- Other


Email content:
{email_content}
"""

# Response Generation Prompts
INTERVIEW_RESPONSE_PROMPT = """
You are a professional job candidate. Based on the following interview-related email, draft a concise and professional response email that:

1. Acknowledges receipt of the interview details
2. Confirms availability for the scheduled time
3. Asks any relevant clarifying questions
4. Expresses enthusiasm for the opportunity
5. Maintains a professional and courteous tone

Keep the response under 150 words and focus on being clear and direct.

Email content:
{email_content}
"""

OFFER_RESPONSE_PROMPT = """
You are a professional job candidate. Based on the following job offer email, draft a professional response that:

1. Expresses genuine gratitude for the offer
2. Acknowledges receipt of all offer details
3. Requests a specific timeframe to review the offer (e.g., "I would appreciate 2-3 business days to review the details")
4. Mentions any specific points you'd like to discuss
5. Maintains a positive and professional tone

Keep the response under 150 words and focus on being appreciative while requesting time to consider.

Email content:
{email_content}
"""

REJECTION_RESPONSE_PROMPT = """
You are a professional job candidate. Based on the following rejection email, draft a polite and professional response that:

1. Expresses genuine gratitude for the opportunity
2. Acknowledges the decision professionally
3. Maintains a positive tone
4. Keeps the door open for future opportunities
5. Shows appreciation for the time and consideration

Keep the response under 100 words and focus on maintaining a positive relationship.

Email content:
{email_content}
""" 