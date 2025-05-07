import pandas as pd
import logging
from typing import List, Dict, Optional
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelClient:
    def __init__(self, excel_file_path: str):
        """
        Initialize Excel client.
        
        Args:
            excel_file_path (str): Path to the Excel file containing candidate data
        """
        self.excel_file_path = excel_file_path
        self.candidates_df = None
        self.email_records_df = None
        self.label_counts_df = None
        self.load_data()

    def load_data(self) -> None:
        """Load data from Excel file."""
        try:
            # Create Excel file with multiple sheets if it doesn't exist
            if not os.path.exists(self.excel_file_path):
                self._create_excel_file()
            
            # Load data from Excel sheets
            self.candidates_df = pd.read_excel(self.excel_file_path, sheet_name=0)
            self.email_records_df = pd.read_excel(self.excel_file_path, sheet_name=0)
            self.label_counts_df = pd.read_excel(self.excel_file_path, sheet_name=0)
            
            logger.info(f"Successfully loaded data from {self.excel_file_path}")
        except Exception as e:
            logger.error(f"Failed to load Excel file: {str(e)}")
            raise

    def _create_excel_file(self) -> None:
        """Create new Excel file with required sheets and columns."""
        # Create DataFrames with required columns
        candidates_df = pd.DataFrame(columns=[
            'Name', 'candidateEmail__c', 'candidatePassword__c'
        ])
        email_records_df = pd.DataFrame(columns=[
            'Id', 'CandidateId', 'GmailMessageId', 'Subject', 'Sender',
            'Category', 'ReceivedAt', 'ProcessedAt', 'ResponseGenerated',
            'ResponseSent'
        ])
        label_counts_df = pd.DataFrame(columns=[
            'Id', 'CandidateId', 'CandidateName', 'CandidateEmail',
            'Application', 'Interview', 'Offer', 'Rejection', 'Other',
            'LastUpdated'
        ])

        # Create Excel writer
        with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
            candidates_df.to_excel(writer, sheet_name='Candidates', index=False)
            email_records_df.to_excel(writer, sheet_name='EmailRecords', index=False)
            label_counts_df.to_excel(writer, sheet_name='LabelCounts', index=False)

    def save_data(self) -> None:
        """Save all data to Excel file."""
        try:
            with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
                self.candidates_df.to_excel(writer, sheet_name='Candidates', index=False)
                self.email_records_df.to_excel(writer, sheet_name='EmailRecords', index=False)
                self.label_counts_df.to_excel(writer, sheet_name='LabelCounts', index=False)
            logger.info(f"Successfully saved data to {self.excel_file_path}")
        except Exception as e:
            logger.error(f"Failed to save Excel file: {str(e)}")
            raise

    def get_candidates(self, limit: int = 150) -> List[Dict]:
        """
        Fetch candidates from Excel file.
        
        Args:
            limit (int): Maximum number of candidates to fetch
            
        Returns:
            List[Dict]: List of candidate records with email and password
        """
        try:
            # Ensure required columns exist
            required_columns = ['Name', 'candidateEmail__c', 'candidatePassword__c']
            missing_columns = [col for col in required_columns if col not in self.candidates_df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns in Excel file: {missing_columns}")

            # Convert DataFrame to list of dictionaries
            candidates = self.candidates_df.head(limit).to_dict('records')
            
            # Add Id field and map column names
            for i, candidate in enumerate(candidates):
                candidate['Id'] = str(i + 1)
                candidate['Email'] = candidate.pop('candidateEmail__c')
                candidate['Password'] = candidate.pop('candidatePassword__c')
            
            logger.info(f"Successfully fetched {len(candidates)} candidates")
            return candidates
        except Exception as e:
            logger.error(f"Failed to fetch candidates: {str(e)}")
            raise

    def get_candidate_by_email(self, email: str) -> Optional[Dict]:
        """
        Fetch a specific candidate by email.
        
        Args:
            email (str): Candidate's email address
            
        Returns:
            Optional[Dict]: Candidate record if found, None otherwise
        """
        try:
            candidate = self.candidates_df[self.candidates_df['candidateEmail__c'] == email]
            if not candidate.empty:
                result = candidate.iloc[0].to_dict()
                result['Id'] = str(candidate.index[0] + 1)
                result['Email'] = result.pop('candidateEmail__c')
                result['Password'] = result.pop('candidatePassword__c')
                return result
            return None
        except Exception as e:
            logger.error(f"Failed to fetch candidate by email: {str(e)}")
            raise

    def update_candidate_status(self, email: str, status: str) -> None:
        """
        Update candidate status in Excel file.
        
        Args:
            email (str): Candidate's email address
            status (str): New status to set
        """
        try:
            self.candidates_df.loc[self.candidates_df['candidateEmail__c'] == email, 'Status'] = status
            self.save_data()
            logger.info(f"Successfully updated status for candidate {email}")
        except Exception as e:
            logger.error(f"Failed to update candidate status: {str(e)}")
            raise

    def add_email_record(self, candidate_id: str, email_data: Dict) -> None:
        """
        Add a new email record.
        
        Args:
            candidate_id (str): Candidate ID
            email_data (Dict): Email data including message ID, subject, etc.
        """
        try:
            new_record = {
                'Id': len(self.email_records_df) + 1,
                'CandidateId': candidate_id,
                'GmailMessageId': email_data['id'],
                'Subject': email_data['subject'],
                'Sender': email_data['sender'],
                'Category': email_data['category'],
                'ReceivedAt': email_data['received_at'],
                'ProcessedAt': datetime.utcnow(),
                'ResponseGenerated': email_data.get('response'),
                'ResponseSent': bool(email_data.get('response'))
            }
            
            self.email_records_df = pd.concat([
                self.email_records_df,
                pd.DataFrame([new_record])
            ], ignore_index=True)
            
            # Update label counts
            self._update_label_count(candidate_id, email_data['category'])
            
            self.save_data()
            logger.info(f"Successfully added email record for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to add email record: {str(e)}")
            raise

    def _update_label_count(self, candidate_id: str, category: str) -> None:
        """
        Update label count for a candidate.
        
        Args:
            candidate_id (str): Candidate ID
            category (str): Email category/label
        """
        try:
            # Get candidate info
            candidate = self.candidates_df.iloc[int(candidate_id) - 1]
            
            # Find existing count record
            mask = self.label_counts_df['CandidateId'] == candidate_id
            
            if mask.any():
                # Update existing record
                self.label_counts_df.loc[mask, category] += 1
                self.label_counts_df.loc[mask, 'LastUpdated'] = datetime.utcnow()
            else:
                # Create new record
                new_count = {
                    'Id': len(self.label_counts_df) + 1,
                    'CandidateId': candidate_id,
                    'CandidateName': candidate['Name'],
                    'CandidateEmail': candidate['candidateEmail__c'],
                    'Application': 0,
                    'Interview': 0,
                    'Offer': 0,
                    'Rejection': 0,
                    'Other': 0,
                    'LastUpdated': datetime.utcnow()
                }
                new_count[category] = 1
                
                self.label_counts_df = pd.concat([
                    self.label_counts_df,
                    pd.DataFrame([new_count])
                ], ignore_index=True)
            
            logger.info(f"Successfully updated label count for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to update label count: {str(e)}")
            raise 