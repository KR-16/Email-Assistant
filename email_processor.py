from googleapiclient.discovery import build
from auth import get_authenticated_services
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

import nltk
nltk.download('punkt_tab', quiet=True)  # Silent download (no prompts)

def summarize_text(text, sentences_count = 1):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return "".join([str(sentence) for sentence in summary])

def fetch_unread_email():
    credential = get_authenticated_services()
    service = build("gmail", "v1", credentials = credential)

    # fetch the unread emails
    results = service.users().messages().list(userId = "me", labelIds = ["INBOX", "UNREAD"]).execute()
    messages = results.get("messages", [])

    email_data = []
    for message in messages:
        email = service.users().messages().get(userId = "me", id = message["id"], format = "full").execute()
        subject = next(h["value"] for h in email["payload"]["headers"] if h["name"] == "Subject")
        body = email["snippet"] # for full body: decode email["payload"]["parts"]

        # Summarize th email
        summary = summarize_text(body)

        email_data.append({
            "subject": subject,
            "summary": summary,
            "id": message["id"]
        })

    return email_data

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
    emails = fetch_unread_email()
    for email in emails:
        # print(f"Subject: {email['subject']}\nSummary: {email['summary']}\n")
        task_title = f"Follow Up: {email['subject']}"
        task_notes = f"Email Summary: \n{email['summary']}"

        create_google_task(task_title, task_notes)
        print(f"Task Created: {task_title}")