from googleapiclient.discovery import build
from auth import get_authenticated_services
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re
import nltk
nltk.download('punkt_tab', quiet=True)  # Silent download (no prompts)

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

def categorize_email(subject, body):
    text = f"{subject.lower()} {body.lower()}"
    for category, keywords in CATEGORIES.items():
        if any(re.search(rf"\b{keywords}\b", text) for keyword in keywords):
            return category
    return "Other"

def extract_job_details(body):
    # Extract the company name
    company = re.search(r"(?:at|from)\s+([A-Z][a-zA-Z\s-]+)", body, re.IGNORECASE)
    company = company.group(1).strip() if company else "Unknown Company"

    # Extract the Job title
    title = re.search(r"(?:role|position)\s+(?:of|as)?\s*([A-Z][a-zA-Z\s-]+)", body, re.IGNORECASE)
    title = title.group(1).strip() if title else "N/A"

    return {"Company": company, "Title": {title}}

def summarize_text(text, sentences_count = 1):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return "".join([str(sentence) for sentence in summary])

def process_emails():
    credential = get_authenticated_services()
    service = build("gmail", "v1", credentials = credential)

    # fetch the unread emails
    results = service.users().messages().list(
        userId = "me", 
        labelIds = ["INBOX", "UNREAD"], 
        maxResults = 10
        ).execute()
    messages = results.get("messages", [])

    email_data = []
    # sheet_data = []
    for message in messages:
        email = service.users().messages().get(
            userId = "me", 
            id = message["id"], 
            format = "full"
            ).execute()
        subject = next(h["value"] for h in email["payload"]["headers"] if h["name"] == "Subject")
        date = next(h["value"] for h in email["payload"]["headers"] if h["name"] == "Date")
        body = email["snippet"] # for full body: decode email["payload"]["parts"]

        # Summarize th email
        summary = summarize_text(body)
        # Categorize Email
        category = categorize_email(subject, body)
        details = extract_job_details(body)

        email_data.append({
            "subject": subject,
            "summary": summary,
            "id": message["id"]
        })

        sheet_data = {
            "date": date,
            "company" : details['Company'],
            "title": details['Title'],
            "category": category,
            "summary": summary,
            "action": "Follow up soon!"
        }
    try:
        export_sheet(sheet_data)
        print("Sheet Exported")
        print(f" Tracked: details {details['company']} - {category}")
    except Exception as e:
        print(f"Sheet export Failed: {e}")

    return email_data

def export_sheet(data):
    credential = get_authenticated_services()
    service = build("sheets","v4", credentials=credential)

    spreadsheet_id = "https://docs.google.com/spreadsheets/d/14qaje3HxAb3VaWZOPNc3Enq2vrEafjQHtaWJ_3bm4PA/edit?usp=sharing"
    range_name = "Job Tracker!A2:F"

    body = {
        "values": [
            [
                data["date"],
                data["company"],
                data["title"],
                data["category"],
                data["summary"],
                data.get("action", "") 
            ]
        ]
    }

    service.spreadsheets().values().append(
        spreadsheetId = spreadsheet_id,
        range = range_name,
        valueInputOption = "USER_ENTERED",
        body = body
    ).execute()


def create_google_task(title, notes):
    credential = get_authenticated_services()
    service = build("tasks", "v1", credentials = credential)

    task = {
        "title":title,
        "notes": notes,
        "status": "needsAction"
    }

    result = service.tasks().insert(tasklist = "@default", body = task).execute()

    return result

if __name__ == "__main__":
    emails = process_emails()
    for email in emails:
        # print(f"Subject: {email['subject']}\nSummary: {email['summary']}\n")
        task_title = f"Follow Up: {email['subject']}"
        task_notes = f"Email Summary: \n{email['summary']}"

        create_google_task(task_title, task_notes)
        print(f"Task Created: {task_title}")