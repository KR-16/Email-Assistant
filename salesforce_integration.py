from simple_salesforce import Salesforce
import os
from dotenv import load_dotenv
from models import Candidate, init_db
from sqlalchemy.orm import sessionmaker

load_dotenv()

class SalesforceConnector:
    def __init__(self):
        self.sf = Salesforce(
            username=os.getenv('SF_USERNAME'),
            password=os.getenv('SF_PASSWORD'),
            security_token=os.getenv('SF_SECURITY_TOKEN'),
            consumer_key=os.getenv('SF_CONSUMER_KEY'),
            consumer_secret=os.getenv('SF_CONSUMER_SECRET')
        )
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)

    def fetch_candidates(self, limit=150):
        """Fetch candidates from Salesforce and store them in the database."""
        try:
            # Query Salesforce for candidates
            query = f"""
                SELECT Id, Email, Name
                FROM Contact
                WHERE Email != null
                LIMIT {limit}
            """
            result = self.sf.query_all(query)
            
            session = self.Session()
            
            for record in result['records']:
                # Check if candidate already exists
                existing_candidate = session.query(Candidate).filter_by(
                    salesforce_id=record['Id']
                ).first()
                
                if not existing_candidate:
                    candidate = Candidate(
                        salesforce_id=record['Id'],
                        email=record['Email'],
                        name=record['Name']
                    )
                    session.add(candidate)
            
            session.commit()
            session.close()
            
            return result['records']
            
        except Exception as e:
            print(f"Error fetching candidates from Salesforce: {str(e)}")
            return []

    def get_candidate_emails(self):
        """Get all candidate emails from the database."""
        session = self.Session()
        candidates = session.query(Candidate).all()
        session.close()
        return [(c.email, c.salesforce_id) for c in candidates] 