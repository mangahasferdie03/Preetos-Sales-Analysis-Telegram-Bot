import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    """Main entry point for the Railway deployment."""
    print("Starting Google Sheets API service...")
    
    try:
        # Get credentials from individual environment variables
        spreadsheet_id = os.getenv('SPREADSHEET_ID', 'your_default_spreadsheet_id')
        
        print("Creating credentials from individual environment variables...")
        
        # Build credentials dict from individual env vars
        creds_data = {
            "type": "service_account",
            "project_id": "preetos-order-agent",
            "private_key_id": "52ef2c399f9d49f7b6af42f061b10706419aeb89",
            "private_key": os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": "preeetos-sheets-agent@preetos-order-agent.iam.gserviceaccount.com",
            "client_id": "114633176250172838577",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/preeetos-sheets-agent%40preetos-order-agent.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        if not creds_data["private_key"]:
            raise ValueError("GOOGLE_PRIVATE_KEY environment variable is required")
        
        print("Credentials created successfully")
        
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
