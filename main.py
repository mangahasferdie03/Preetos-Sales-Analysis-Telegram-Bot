import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    """Main entry point for the Railway deployment."""
    print("Starting Google Sheets API service...")
    
    try:
        # Get credentials from environment variable
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        spreadsheet_id = os.getenv('SPREADSHEET_ID', 'your_default_spreadsheet_id')
        
        if not credentials_json:
            raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is required")
        
        print("Creating credentials from environment variable...")
        
        # Create credentials directly from environment variable
        # Parse the JSON string with proper error handling
        try:
            # Handle potential escaping issues
            if credentials_json.startswith('"') and credentials_json.endswith('"'):
                credentials_json = credentials_json[1:-1]  # Remove outer quotes
            
            # Replace escaped quotes
            credentials_json = credentials_json.replace('\\"', '"')
            
            creds_data = json.loads(credentials_json)
            print("JSON parsed successfully")
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"First 100 chars of credentials: {credentials_json[:100]}")
            raise
        
        # Create credentials object directly
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_info(
            creds_data, scopes=scopes
        )
        
        # Build the service
        service = build('sheets', 'v4', credentials=creds)
        print("Google Sheets service created successfully")
        
        # Test connection
        print(f"Testing connection to spreadsheet: {spreadsheet_id}")
        sheet = service.spreadsheets()
        
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
