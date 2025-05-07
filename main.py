from dotenv import load_dotenv
load_dotenv()

class EmailProcessor:
    """
    Main Orchestrator class that coordinates the entire email processing workflow.
    Integrating Salesforce, Gmail, ChatGPT functionality
    """

    def __init__(self):
        """
        Initialize all required connectors and services
        """
        # Salesforce
        self.sf_connector = SalesForceConnector()

        # Gmail
        self.gmail_connector = GmailConnector()
        
        #ChatGpt
        self.chatgpt_processor = ChatGPTProcessor()

        #database
        self.engine = init_db()
        self.Session = sessionmaker(bind = self.engine)

    def process_emails(self):
        """
        Method to process emails for all candidates
        1. Authenticate Gmail
        2. Fetch candidates from Salesforce
        3. Process emails for each candidates
        4. Categorize the emails using AI
        5. Generate and stores responses
        6. Updates email statistics
        """

        try:
            # Autenticate Gmail API
            self.gmail_connector.authenticate()
