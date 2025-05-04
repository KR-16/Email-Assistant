# Import required libraries
from simple_salesforce import Salesforce
import os
from dotenv import load_dotenv
from models import Candidate, init_db
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

class SalesforceConnector:
    """
    Handles all interactions with Salesforce CRM.
    Provides methods to fetch and manage candidate data.
    """
    def __init__(self):
        """
        Initialize Salesforce connection and database session.
        Uses credentials from environment variables.
        """
        # Initialize Salesforce connection with credentials
        self.sf = Salesforce(
            username=os.getenv('SF_USERNAME'),
            password=os.getenv('SF_PASSWORD'),
            security_token=os.getenv('SF_SECURITY_TOKEN'),
            consumer_key=os.getenv('SF_CONSUMER_KEY'),
            consumer_secret=os.getenv('SF_CONSUMER_SECRET')
        )
        # Initialize database connection
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)

    def fetch_candidates(self, limit=150):
        """
        Fetch candidates from Salesforce and store them in the database.
        
        Args:
            limit (int): Maximum number of candidates to fetch (default: 150)
            
        Returns:
            list: List of candidate records from Salesforce
        """
        try:
            # Query Salesforce for candidates with email addresses
            query = f"""
                SELECT Id, Email, Name
                FROM Contact
                WHERE Email != null
                LIMIT {limit}
            """
            result = self.sf.query_all(query)
            
            # Create database session
            session = self.Session()
            
            # Process each candidate record
            for record in result['records']:
                # Check if candidate already exists in database
                existing_candidate = session.query(Candidate).filter_by(
                    salesforce_id=record['Id']
                ).first()
                
                # Add new candidate if not exists
                if not existing_candidate:
                    candidate = Candidate(
                        salesforce_id=record['Id'],
                        email=record['Email'],
                        name=record['Name']
                    )
                    session.add(candidate)
            
            # Commit changes to database
            session.commit()
            session.close()
            
            return result['records']
            
        except Exception as e:
            print(f"Error fetching candidates from Salesforce: {str(e)}")
            return []

    def get_candidate_emails(self):
        """
        Get all candidate emails from the database.
        
        Returns:
            list: List of tuples containing (email, salesforce_id)
        """
        # Create database session
        session = self.Session()
        # Query all candidates
        candidates = session.query(Candidate).all()
        session.close()
        # Return list of (email, salesforce_id) tuples
        return [(c.email, c.salesforce_id) for c in candidates] 