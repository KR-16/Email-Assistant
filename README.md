# Email Assistant

An automated system that connects Salesforce CRM, Gmail, and ChatGPT to process candidate-related emails and respond accordingly.

## Features

- Fetches candidate data from Salesforce CRM
- Processes emails from Gmail accounts
- Categorizes emails using ChatGPT
- Generates appropriate responses based on email categories
- Stores email statistics and responses in a database
- Applies Gmail labels automatically

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd email-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in all required credentials:
     - Salesforce credentials
     - OpenAI API key
     - Database credentials
     - Gmail API credentials

4. Set up Gmail API:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials and save as `credentials.json`

5. Set up database:
   - Create a PostgreSQL database
   - Update database credentials in `.env`

## Usage

1. Run the email processor:
```bash
python email_processor.py
```

The system will:
- Fetch candidates from Salesforce
- Process their emails
- Categorize emails using ChatGPT
- Generate responses where appropriate
- Store statistics in the database

## Email Categories

- **Application**: Emails about job applications or resume submissions
- **Interview**: Emails about scheduling, confirming, or following up on interviews
- **Offer**: Emails containing job offers or employment terms
- **Rejection**: Emails communicating candidate rejection
- **Other**: Emails that don't fit other categories

## Security Notes

- Never commit `.env` file or `credentials.json` to version control
- Use OAuth for Gmail authentication
- Store sensitive credentials securely
- Follow best practices for API key management

## Error Handling

The system includes comprehensive error handling for:
- API authentication failures
- Network issues
- Database connection problems
- Email processing errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.