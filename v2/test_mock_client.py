from src.openai.mock_client import MockOpenAIClient

def test_email_processing():
    # Create mock client
    client = MockOpenAIClient()
    
    # Test emails
    test_emails = [
        {
            "subject": "Interview Invitation",
            "content": """
            Dear Candidate,
            
            We would like to invite you for an interview for the Software Engineer position.
            Please let us know your availability for next week.
            
            Best regards,
            HR Team
            """
        },
        {
            "subject": "Job Offer",
            "content": """
            Congratulations!
            
            We are pleased to offer you the position of Software Engineer at our company.
            Please review the attached offer letter and let us know your decision.
            
            Best regards,
            HR Team
            """
        },
        {
            "subject": "Application Status",
            "content": """
            Dear Candidate,
            
            Unfortunately, we have decided to move forward with other candidates for the position.
            We appreciate your interest in our company.
            
            Best regards,
            HR Team
            """
        }
    ]
    
    # Process each test email
    for email in test_emails:
        print(f"\nProcessing email: {email['subject']}")
        print("-" * 50)
        
        # Categorize email
        category = client.categorize_email(email['content'])
        print(f"Category: {category}")
        
        # Generate response
        response = client.generate_response(email['content'], category)
        if response:
            print("\nGenerated Response:")
            print(response)
        
        print("-" * 50)

if __name__ == "__main__":
    test_email_processing() 