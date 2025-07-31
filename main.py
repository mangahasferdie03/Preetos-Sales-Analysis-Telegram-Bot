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
            # Save credentials to temporary file for the client
            with open('temp_credentials.json', 'w') as f:
                f.write(credentials_json)
            credentials_path = 'temp_credentials.json'
        else:
            credentials_path = 'credentials.json'
            print("Using credentials from file")
        
        # Initialize client
        client = GoogleSheetsClient(credentials_path=credentials_path)
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
        raise

if __name__ == "__main__":
    main()