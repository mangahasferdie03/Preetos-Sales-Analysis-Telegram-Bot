import os
import json
from google_sheets_client import GoogleSheetsClient

def main():
    """Main entry point for the Railway deployment."""
    print("Starting Google Sheets API service...")
    
    # Initialize the Google Sheets client
    try:
        # Check if we have credentials in environment variable
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if credentials_json:
            print("Using credentials from environment variable")
            # Parse the JSON string and write it properly formatted
            try:
                creds_data = json.loads(credentials_json)
                with open('temp_credentials.json', 'w') as f:
                    json.dump(creds_data, f, indent=2)
                credentials_file = 'temp_credentials.json'
                print("Credentials file created successfully")
            except json.JSONDecodeError as e:
                print(f"Error parsing credentials JSON: {e}")
                raise
        else:
            credentials_file = 'credentials.json'
            print("Using credentials from file")
        
        # Get spreadsheet ID from environment or use a default
        spreadsheet_id = os.getenv('SPREADSHEET_ID', 'your_default_spreadsheet_id')
        print(f"Using spreadsheet ID: {spreadsheet_id}")
        
        # Initialize client
        client = GoogleSheetsClient(
            credentials_file=credentials_file,
            spreadsheet_id=spreadsheet_id
        )
        print("Google Sheets client initialized successfully")
        
        # Basic health check - you can customize this
        print("Service is running and ready to handle requests")
        
        # Keep the service alive
        import time
        while True:
            print("Service heartbeat - Google Sheets API ready")
            time.sleep(300)  # Print status every 5 minutes
            
    except Exception as e:
        print(f"Error starting service: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
