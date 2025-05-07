"""
Excel Client Module
==================

This module provides functionality to interact with Excel files for data storage and retrieval.
It manages three main sheets:
1. Candidates: Stores candidate information
2. EmailRecords: Tracks email processing history
3. LabelCounts: Maintains counts of email categories

The client handles:
- Reading and writing Excel data
- Managing multiple sheets
- Tracking email records
- Counting email categories

Author: Your Name
Date: 2024
"""

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
    """
    Client for interacting with Excel files.
    
    This class provides methods to:
    - Load and save Excel data
    - Manage candidate information
    - Track email records
    - Count email categories
    
    Attributes:
        excel_file_path (str): Path to the Excel file
        candidates_df (pd.DataFrame): DataFrame for candidate data
        email_records_df (pd.DataFrame): DataFrame for email records
        label_counts_df (pd.DataFrame): DataFrame for label counts
    """
    
    def __init__(self, excel_file_path: str):
        """
        Initialize Excel client.
        
        Args:
            excel_file_path (str): Path to the Excel file containing candidate data
            
        Note:
            - Creates Excel file if it doesn't exist
            - Loads data from all sheets
            - Initializes DataFrames
        """
        self.excel_file_path = excel_file_path
        self.candidates_df = None
        self.email_records_df = None
        self.label_counts_df = None
        self.load_data()

    def load_data(self) -> None:
        """
        Load data from Excel file.
        
        This method:
        1. Creates Excel file if it doesn't exist
        2. Loads candidate data from Candidates sheet
        3. Loads or initializes Results sheet for label counts
        
        Note:
            - Reads candidates from Candidates sheet
            - Maintains label counts in Results sheet
            - Handles file creation and loading
        """
        try:
            # Create Excel file if it doesn't exist
            if not os.path.exists(self.excel_file_path):
                self._create_excel_file()
            
            # Load data from Excel sheets
            try:
                # Try to load the first sheet as Candidates
                self.candidates_df = pd.read_excel(self.excel_file_path, sheet_name=0)
                
                # Verify if it has the required columns
                required_columns = ['Name', 'candidateEmail__c', 'candidatePassword__c']
                if not all(col in self.candidates_df.columns for col in required_columns):
                    raise ValueError("First sheet does not have required candidate columns")
                
                # Initialize empty DataFrames for other sheets
                self.email_records_df = pd.DataFrame(columns=[
                    'Id', 'CandidateId', 'GmailMessageId', 'Subject', 'Sender',
                    'Category', 'ReceivedAt', 'ProcessedAt', 'ResponseGenerated',
                    'ResponseSent'
                ])
                
                self.label_counts_df = pd.DataFrame(columns=[
                    'Id', 'CandidateId', 'CandidateName', 'CandidateEmail',
                    'Application', 'Interview', 'Offer', 'Rejection', 'Other',
                    'LastUpdated'
                ])
                
                # Save to create the new sheets
                self.save_data()
                
            except Exception as e:
                logger.error(f"Error loading Excel file: {str(e)}")
                raise
            
            logger.info(f"Successfully loaded data from {self.excel_file_path}")
        except Exception as e:
            logger.error(f"Failed to load Excel file: {str(e)}")
            raise

    def _create_excel_file(self) -> None:
        """
        Create new Excel file with required sheets.
        
        Creates two sheets:
        1. Candidates:
           - Name
           - candidateEmail__c
           - candidatePassword__c
           
        2. Results:
           - CandidateId
           - CandidateName
           - CandidateEmail
           - Application
           - Interview
           - Offer
           - Rejection
           - Other
           - LastUpdated
        """
        # Create DataFrames for each sheet
        candidates_df = pd.DataFrame(columns=[
            'Name', 'candidateEmail__c', 'candidatePassword__c'
        ])
        
        results_df = pd.DataFrame(columns=[
            'CandidateId', 'CandidateName', 'CandidateEmail',
            'Application', 'Interview', 'Offer', 'Rejection', 'Other',
            'LastUpdated'
        ])

        # Create Excel file with both sheets
        with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
            candidates_df.to_excel(writer, sheet_name='Candidates', index=False)
            results_df.to_excel(writer, sheet_name='Results', index=False)

    def save_data(self) -> None:
        """
        Save data to Excel file.
        
        This method:
        1. Saves candidate data to Candidates sheet
        2. Saves label counts to Results sheet
        
        Note:
            - Maintains separate sheets
            - Preserves existing data
            - Updates all changes
        """
        try:
            with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
                self.candidates_df.to_excel(writer, sheet_name='Candidates', index=False)
                self.label_counts_df.to_excel(writer, sheet_name='Results', index=False)
            
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
            List[Dict]: List of candidate records with:
                - Id: Generated ID
                - Name: Candidate name
                - Email: Candidate email
                - Password: candidatePassword__c
                
        Note:
            - Validates required columns
            - Maps column names
            - Generates IDs
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
            
        Note:
            - Searches by email address
            - Maps column names
            - Generates ID
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
        Add a new email record and update label count.
        
        Args:
            candidate_id (str): Candidate ID
            email_data (Dict): Email data including:
                - id: Gmail message ID
                - subject: Email subject
                - sender: Sender's email
                - category: Email category
                - received_at: Reception time
                - response: Generated response
                
        Note:
            - Updates label counts
            - Saves changes
        """
        try:
            # Update label counts
            self._update_label_count(candidate_id, email_data['category'])
            
            logger.info(f"Successfully processed email for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to process email: {str(e)}")
            raise

    def _update_label_count(self, candidate_id: str, category: str) -> None:
        """
        Update label count for a candidate.
        
        Args:
            candidate_id (str): Candidate ID
            category (str): Email category/label
            
        Note:
            - Updates existing count or creates new record
            - Tracks all label types
            - Updates timestamp
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
            
            # Save changes
            self.save_data()
            logger.info(f"Successfully updated label count for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to update label count: {str(e)}")
            raise 