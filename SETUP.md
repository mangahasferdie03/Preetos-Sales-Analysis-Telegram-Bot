# Setup Guide

## Quick Start

Follow these steps to get your Preetos Sales Analysis Telegram Bot up and running.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Google Sheets API

### Option A: Service Account (Recommended for Production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Google Sheets API
4. Go to "Credentials" → "Create Credentials" → "Service Account"
5. Create a service account and download the JSON key file
6. Save it as `credentials.json` in the project root
7. Share your Google Sheet with the service account email (found in the JSON file)

### Option B: OAuth 2.0 (For Local Development)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Google Sheets API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Choose "Desktop app" as the application type
6. Download the credentials JSON file
7. Save it as `credentials.json` in the project root

## Step 3: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided by BotFather

## Step 4: Get Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key

## Step 5: Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your values:

```env
# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
SPREADSHEET_ID=your_spreadsheet_id_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### How to Find Your Spreadsheet ID

The Spreadsheet ID is in the URL of your Google Sheet:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```

## Step 6: Run the Bot

### Local Development

```bash
python telegram_bot.py
```

### Test the Google Sheets Connection

```bash
python example_usage.py
```

## Step 7: Test Your Bot

1. Open Telegram
2. Search for your bot using the username you created
3. Send `/start` to begin
4. Try commands:
   - `/sales_today`
   - `/sales_this_week`
   - `/sales_customdate`

## Deployment to Railway

### Step 1: Prepare Credentials

Convert your `credentials.json` to base64:

```bash
base64 -i credentials.json | tr -d '\n'
```

Copy the output.

### Step 2: Set Environment Variables in Railway

Add these variables in your Railway project:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `SPREADSHEET_ID`: Your Google Sheets spreadsheet ID
- `GOOGLE_CREDENTIALS_B64`: The base64-encoded credentials from Step 1

### Step 3: Deploy

Railway will automatically detect the `Procfile` and deploy your bot.

## Troubleshooting

### Error: "Credentials file path is required"

Make sure your `.env` file exists and contains the correct path to `credentials.json`.

### Error: "Spreadsheet ID is required"

Add your spreadsheet ID to the `.env` file.

### Error: "Permission denied" when accessing Google Sheets

Make sure you've shared your Google Sheet with the service account email (found in `credentials.json`).

### Bot doesn't respond to commands

1. Check that the bot is running (`python telegram_bot.py`)
2. Verify the Telegram token is correct
3. Check the console for error messages

### Claude AI not responding

Verify your Anthropic API key is correct and has available credits.

## File Structure

```
.
├── google_sheets_client.py       # Google Sheets API client
├── telegram_bot.py                # Telegram bot (main application)
├── main.py                        # Railway deployment entry point
├── example_usage.py               # Test Google Sheets connection
├── requirements.txt               # Python dependencies
├── .env                           # Your configuration (not in git)
├── .env.example                   # Example configuration
├── credentials.json               # Google credentials (not in git)
└── README.md                      # Documentation
```

## Next Steps

1. Customize the bot commands in `telegram_bot.py`
2. Adjust the Google Sheets column mappings in the code
3. Add more analytics features
4. Deploy to production (Railway, Heroku, etc.)

## Support

If you encounter issues, check:
- Console error messages
- Google Cloud Console for API quotas
- Telegram Bot API status
- Anthropic API status

Happy analyzing!
