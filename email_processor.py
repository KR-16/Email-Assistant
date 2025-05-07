from googleapiclient.discovery import build
from auth import get_authenticated_services
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re
import nltk
nltk.download('punkt_tab', quiet=True)  # Silent download (no prompts)
from salesforce_integration import SalesforceConnector
from gmail_integration import GmailConnector
from chatgpt_integration import ChatGPTProcessor
from models import EmailStats, init_db
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = {
    "Job Application": [
        "application", "hiring", "recruiter", "job", "role", 
        "position", "career", "resume", "cv", "interview",
        "opportunity", "apply", "referral", "linkedin"
    ],
    "Rejection": ["regret", "unfortunately", "not proceed", "other candidates"],
    "Interview": ["interview", "zoom", "meet", "schedule", "calendar"],
    "Offer": ["offer", "congratulations", "welcome aboard", "compensation"],
    "Networking": ["connect", "coffee chat", "referral", "linkedin"],
    "Other": []
}

# def categorize_email(subject, body):
#     text = f"{subject.lower()} {body.lower()}"
#     for category, keywords in CATEGORIES.items():
#         if any(re.search(rf"\b{keywords}\b", text) for keyword in keywords):
#             return category
#     return "Other"

# def extract_job_details(body):
#     # Extract the company name
#     company = re.search(r"(?:at|from)\s+([A-Z][a-zA-Z\s-]+)", body, re.IGNORECASE)
#     company = company.group(1).strip() if company else "Unknown Company"

#     # Extract the Job title
#     title = re.search(r"(?:role|position)\s+(?:of|as)?\s*([A-Z][a-zA-Z\s-]+)", body, re.IGNORECASE)
#     title = title.group(1).strip() if title else "N/A"

#     return {"Company": company, "Title": {title}}

# def summarize_text(text, sentences_count = 1):
#     parser = PlaintextParser.from_string(text, Tokenizer("english"))
#     summarizer = LsaSummarizer()
#     summary = summarizer(parser.document, sentences_count)
#     return "".join([str(sentence) for sentence in summary])

# def process_emails():
#     credential = get_authenticated_services()
#     service = build("gmail", "v1", credentials = credential)

#     # fetch the unread emails
#     results = service.users().messages().list(
#         userId = "me", 
#         labelIds = ["INBOX", "UNREAD"], 
#         maxResults = 10
#         ).execute()
#     messages = results.get("messages", [])

#     email_data = []
#     # sheet_data = []
#     for message in messages:
#         email = service.users().messages().get(
#             userId = "me", 
#             id = message["id"], 
#             format = "full"
#             ).execute()
#         subject = next(h["value"] for h in email["payload"]["headers"] if h["name"] == "Subject")
#         date = next(h["value"] for h in email["payload"]["headers"] if h["name"] == "Date")
#         body = email["snippet"] # for full body: decode email["payload"]["parts"]

#         # Summarize th email
#         summary = summarize_text(body)
#         # Categorize Email
#         category = categorize_email(subject, body)
#         details = extract_job_details(body)

#         email_data.append({
#             "subject": subject,
#             "summary": summary,
#             "id": message["id"]
#         })

#         sheet_data = {
#             "date": date,
#             "company" : details['Company'],
#             "title": details['Title'],
#             "category": category,
#             "summary": summary,
#             "action": "Follow up soon!"
#         }
#     try:
#         export_sheet(sheet_data)
#         print("Sheet Exported")
#         print(f" Tracked: details {details['company']} - {category}")
#     except Exception as e:
#         print(f"Sheet export Failed: {e}")

#     return email_data

# def export_sheet(data):
#     credential = get_authenticated_services()
#     service = build("sheets","v4", credentials=credential)

#     spreadsheet_id = "https://docs.google.com/spreadsheets/d/14qaje3HxAb3VaWZOPNc3Enq2vrEafjQHtaWJ_3bm4PA/edit?usp=sharing"
#     range_name = "Job Tracker!A2:F"

#     body = {
#         "values": [
#             [
#                 data["date"],
#                 data["company"],
#                 data["title"],
#                 data["category"],
#                 data["summary"],
#                 data.get("action", "") 
#             ]
#         ]
#     }

#     service.spreadsheets().values().append(
#         spreadsheetId = spreadsheet_id,
#         range = range_name,
#         valueInputOption = "USER_ENTERED",
#         body = body
#     ).execute()


# def create_google_task(title, notes):
#     credential = get_authenticated_services()
#     service = build("tasks", "v1", credentials = credential)

#     task = {
#         "title":title,
#         "notes": notes,
#         "status": "needsAction"
#     }

#     result = service.tasks().insert(tasklist = "@default", body = task).execute()

#     return result

class EmailProcessor:
    """
    Main orchestrator class that coordinates the entire email processing workflow.
    Integrates Salesforce, Gmail, and ChatGPT functionality.
    """
    def __init__(self):
        """Initialize all required connectors and services."""
        # Initialize Salesforce connector
        self.sf_connector = SalesforceConnector()
        # Initialize Gmail connector
        self.gmail_connector = GmailConnector()
        # Initialize ChatGPT processor
        self.chatgpt_processor = ChatGPTProcessor()
        # Initialize database connection
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)

    def process_emails(self):
        """
        Main method to process emails for all candidates.
        Orchestrates the entire workflow:
        1. Authenticates with Gmail
        2. Fetches candidates from Salesforce
        3. Processes emails for each candidate
        4. Categorizes emails using ChatGPT
        5. Generates and stores responses
        6. Updates email statistics
        """
        try:
            # Authenticate with Gmail API
            self.gmail_connector.authenticate()
            
            # Get all candidate emails from database
            candidates = self.sf_connector.get_candidate_emails()
            
            # Process emails for each candidate
            for email, salesforce_id in candidates:
                print(f"Processing emails for candidate: {email}")
                
                # Get today's emails for the candidate
                messages = self.gmail_connector.get_today_emails()
                
                # Initialize counters for email categories
                category_counts = {
                    "Application": 0,
                    "Interview": 0,
                    "Offer": 0,
                    "Rejection": 0,
                    "Other": 0
                }
                
                # Process each email
                for message in messages:
                    # Get email content
                    email_content = self.gmail_connector.get_email_content(message['id'])
                    
                    if not email_content:
                        continue
                    
                    # Categorize email using ChatGPT
                    category = self.chatgpt_processor.categorize_email(email_content)
                    
                    # Apply Gmail label
                    self.gmail_connector.apply_label(message['id'], category)
                    
                    # Update category counter
                    category_counts[category] += 1
                    
                    # Generate and store response if needed
                    if category != "Other":
                        response_draft = self.chatgpt_processor.generate_response(
                            email_content, category
                        )
                        
                        if response_draft:
                            self.chatgpt_processor.store_response(
                                salesforce_id,
                                message['id'],
                                category,
                                response_draft
                            )
                
                # Store email statistics for the candidate
                self._store_email_stats(salesforce_id, category_counts)
                
        except Exception as e:
            print(f"Error processing emails: {str(e)}")

    def _store_email_stats(self, candidate_id, category_counts):
        """
        Store email statistics in the database.
        
        Args:
            candidate_id (int): ID of the candidate
            category_counts (dict): Dictionary containing counts for each email category
        """
        try:
            # Create database session
            session = self.Session()
            
            # Create new stats record
            stats = EmailStats(
                candidate_id=candidate_id,
                application_count=category_counts["Application"],
                interview_count=category_counts["Interview"],
                offer_count=category_counts["Offer"],
                rejection_count=category_counts["Rejection"],
                other_count=category_counts["Other"]
            )
            
            # Save to database
            session.add(stats)
            session.commit()
            session.close()
            
        except Exception as e:
            print(f"Error storing email stats: {str(e)}")

if __name__ == "__main__":
    # Create and run email processor
    processor = EmailProcessor()
    processor.process_emails()