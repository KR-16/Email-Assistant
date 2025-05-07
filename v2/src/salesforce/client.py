from simple_salesforce import Salesforce
import logging
from typing import List, Dict
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import (
    SALESFORCE_USERNAME,
    SALESFORCE_PASSWORD,
    SALESFORCE_SECURITY_TOKEN
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SalesforceClient:
    def __init__(self):
        self.sf = None
        self.connect()

    def connect(self) -> None:
        """Establish connection to Salesforce CRM."""
        try:
            self.sf = Salesforce(
                username=SALESFORCE_USERNAME,
                password=SALESFORCE_PASSWORD,
                security_token=SALESFORCE_SECURITY_TOKEN
            )
            logger.info("Successfully connected to Salesforce")
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {str(e)}")
            raise

    def get_candidates(self, limit: int = 150) -> List[Dict]:
        """
        Fetch candidates from Salesforce CRM.
        
        Args:
            limit (int): Maximum number of candidates to fetch
            
        Returns:
            List[Dict]: List of candidate records with email and other details
        """
        try:
            query = f"""
                SELECT Id, Email, Name, Phone, Status__c
                FROM Contact
                WHERE Email != null
                LIMIT {limit}
            """
            result = self.sf.query(query)
            candidates = result['records']
            logger.info(f"Successfully fetched {len(candidates)} candidates")
            return candidates
        except Exception as e:
            logger.error(f"Failed to fetch candidates: {str(e)}")
            raise

    def update_candidate_status(self, candidate_id: str, status: str) -> None:
        """
        Update candidate status in Salesforce.
        
        Args:
            candidate_id (str): Salesforce Contact ID
            status (str): New status to set
        """
        try:
            self.sf.Contact.update(candidate_id, {'Status__c': status})
            logger.info(f"Successfully updated status for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to update candidate status: {str(e)}")
            raise

    def get_candidate_by_email(self, email: str) -> Dict:
        """
        Fetch a specific candidate by email.
        
        Args:
            email (str): Candidate's email address
            
        Returns:
            Dict: Candidate record if found, None otherwise
        """
        try:
            query = f"""
                SELECT Id, Email, Name, Phone, Status__c
                FROM Contact
                WHERE Email = '{email}'
                LIMIT 1
            """
            result = self.sf.query(query)
            if result['records']:
                return result['records'][0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch candidate by email: {str(e)}")
            raise 