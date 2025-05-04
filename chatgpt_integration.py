import openai
import os
from dotenv import load_dotenv
from models import EmailResponse, init_db
from sqlalchemy.orm import sessionmaker

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class ChatGPTProcessor:
    def __init__(self):
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)

    def categorize_email(self, email_content):
        """Categorize email content using ChatGPT."""
        try:
            prompt = f"""Read the following email content and categorize it into one of the following labels:
            - Application – If the email is about applying for a job or submitting a resume.
            - Interview – If the email is about scheduling, confirming, or following up on an interview.
            - Offer – If the email contains a job offer or discussion of employment terms.
            - Rejection – If the email communicates that the candidate is not selected or rejected.
            - Other – If the email doesn't clearly fit into any of the above categories.

            Respond with only the label name (Application, Interview, Offer, Rejection, Other).

            Email content:
            {email_content}
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email categorization assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )

            category = response.choices[0].message.content.strip()
            return category

        except Exception as e:
            print(f"Error categorizing email: {str(e)}")
            return "Other"

    def generate_response(self, email_content, category):
        """Generate an appropriate response based on the email category."""
        try:
            if category == "Other":
                return None

            prompt = f"""Based on the following email content and its category ({category}), 
            draft a professional and appropriate response email. The response should be:
            - Professional and courteous
            - Relevant to the email content
            - Appropriate for the category
            - Concise and clear

            Email content:
            {email_content}

            Please provide only the body of the response email, without any headers or signatures.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email response assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None

    def store_response(self, candidate_id, email_id, category, response_draft):
        """Store the generated response in the database."""
        try:
            session = self.Session()
            
            email_response = EmailResponse(
                candidate_id=candidate_id,
                email_id=email_id,
                category=category,
                response_draft=response_draft
            )
            
            session.add(email_response)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            print(f"Error storing response: {str(e)}")
            return False 