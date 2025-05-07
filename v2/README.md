# Email Assistant v2

An automated system that connects Salesforce CRM, Gmail, and ChatGPT to process candidate-related emails and respond accordingly.

## Features

- Salesforce CRM integration for candidate data
- Gmail API integration for email processing
- Automated email categorization using ChatGPT
- Smart email response generation
- Database storage for tracking and analytics

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
Create a `.env` file with the following variables:
```
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_database_url
```

3. Set up Gmail API:
- Go to Google Cloud Console
- Create a new project
- Enable Gmail API
- Create OAuth 2.0 credentials
- Download the credentials file and save as `credentials.json`

## Project Structure

```
├── config/
│   └── config.py
├── src/
│   ├── salesforce/
│   │   └── client.py
│   ├── gmail/
│   │   └── client.py
│   ├── openai/
│   │   └── client.py
│   └── database/
│       └── models.py
├── main.py
├── requirements.txt
└── README.md
```

## Usage

Run the main script:
```bash
python main.py
```

## Security Notes

- All credentials are stored in environment variables
- Gmail authentication uses OAuth 2.0
- Database connections are encrypted
- API keys are never stored in plain text

## License

MIT License 