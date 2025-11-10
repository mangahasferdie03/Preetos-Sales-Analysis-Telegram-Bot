# Preetos Sales Analysis Telegram Bot

A Python-based Telegram bot that integrates with Google Sheets API and Claude AI to provide sales analysis and insights for Preetos orders.

## Features

- **Direct Google Sheets Integration**: Connect to Google Sheets API with easy-to-use methods
- **Sales Analytics**: Daily, weekly, and custom date range sales reports
- **AI-Powered Insights**: Claude AI integration for intelligent sales analysis
- **Scheduled Reports**: Automated daily sales reports at 3 PM and 11 PM
- **Revenue Tracking**: Payment and delivery status monitoring
- **Product Inventory**: Track pouches and tubs across multiple flavors
- **Performance Metrics**: 7-day average, 30-day average, target streaks

## Core Methods

- `read_sheet()` - Retrieve spreadsheet data
- `write_sheet()` - Store data to sheets
- `append_sheet()` - Add rows to existing data
- `clear_sheet()` - Remove sheet contents
- `get_sheet_info()` - Fetch metadata

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

1. Create a new project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API
3. Create OAuth 2.0 credentials or Service Account credentials
4. Download the credentials JSON file and save it as `credentials.json`

### 3. Local Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and add:
- Path to your Google credentials file
- Your Google Sheets spreadsheet ID
- Your Telegram bot token (from [@BotFather](https://t.me/botfather))
- Your Anthropic API key

## Authentication

The system uses OAuth 2.0, automatically prompting browser-based authentication on initial execution. Upon successful authorization, the client generates a persistent `token.json` file for subsequent operations without re-authentication.

For production deployments (like Railway), the bot supports base64-encoded credentials via the `GOOGLE_CREDENTIALS_B64` environment variable.

## Usage

### Running Locally

```bash
python telegram_bot.py
```

### Running with Railway

Set the following environment variables in your Railway project:
- `TELEGRAM_BOT_TOKEN`
- `ANTHROPIC_API_KEY`
- `GOOGLE_CREDENTIALS_B64` (base64 encoded credentials JSON)
- `SPREADSHEET_ID`

Deploy using the `Procfile`:
```
web: python telegram_bot.py
```

### Telegram Bot Commands

- `/today` - Get today's sales analysis
- `/custom` - Analyze sales for custom date ranges

### Scheduled Reports

The bot can automatically send daily sales reports at **3 PM and 11 PM** to a specified chat.

**Setup:**
1. Get your Telegram Chat ID (use @userinfobot or check bot logs)
2. Add to your `.env`:
   ```env
   REPORT_CHAT_ID=your_chat_id_here
   TIMEZONE=Asia/Manila
   ```
3. Restart the bot

For detailed setup instructions, see [SCHEDULED_REPORTS.md](SCHEDULED_REPORTS.md)

## Technologies

- **Python** (100% of codebase)
- Google Sheets API for data connectivity
- Telegram Bot API for messaging interface
- Pandas for data manipulation
- Claude AI (Anthropic) for sales insights

## Error Handling

The library incorporates error handling for typical failure scenarios including:
- Authentication issues
- Invalid spreadsheet references
- Connectivity problems
- Missing configuration files

## Project Structure

```
.
├── google_sheets_client.py       # Google Sheets API client
├── telegram_bot.py                # Telegram bot implementation
├── main.py                        # Railway deployment entry point
├── example_usage.py               # Usage examples
├── requirements.txt               # Python dependencies
├── Procfile                       # Railway/Heroku deployment config
├── .env.example                   # Environment variables template
├── .gitignore                     # Git exclusion rules
├── Google_Sheet_Column_Descriptions_Labeled.txt  # Data schema reference
└── README.md                      # This file
```

## Example Code

```python
from google_sheets_client import GoogleSheetsClient

# Initialize client
client = GoogleSheetsClient()

# Read data from sheet
data = client.read_sheet(range_name='A1:E10', sheet_name='ORDER')

# Write data
sample_data = [
    ['Name', 'Age', 'City'],
    ['Alice', 25, 'New York'],
    ['Bob', 30, 'London']
]
client.write_sheet(data=sample_data, range_name='G1', sheet_name='ORDER')

# Append new row
new_row = [['Charlie', 35, 'Tokyo']]
client.append_sheet(data=new_row, sheet_name='ORDER')
```

## License

This project is for personal/business use.

## Support

For issues or questions, please open an issue in the repository.
