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

        # Try multiple approaches to get credentials

        # Approach 1: Try base64 encoded full JSON
        credentials_b64 = os.getenv('GOOGLE_CREDENTIALS_B64')
        if credentials_b64:
            print("Using base64 encoded credentials...")
            import base64
            try:
                credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
                creds_data = json.loads(credentials_json)
                print("Base64 credentials parsed successfully")
            except Exception as e:
                print(f"Base64 parsing failed: {e}")
                credentials_b64 = None

        if not credentials_b64:
            # Approach 2: Build from individual environment variables with multiple newline handling
            print("Using individual environment variables...")
            raw_private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')

            if not raw_private_key:
                raise ValueError("Either GOOGLE_CREDENTIALS_B64 or GOOGLE_PRIVATE_KEY environment variable is required")

            print(f"Raw private key length: {len(raw_private_key)}")
            print(f"First 100 chars: {raw_private_key[:100]}")
            print(f"Last 100 chars: {raw_private_key[-100:]}")

            # Try different newline replacements
            private_key_attempts = [
                raw_private_key.replace('\\n', '\n'),  # Replace literal \n with actual newlines
                raw_private_key.replace('\\\\n', '\n'),  # Replace escaped \\n
                raw_private_key,  # Use as-is (maybe it already has real newlines)
                raw_private_key.replace('\n', '\n'),  # No change, but test anyway
            ]

            creds_data = {
                "type": "service_account",
                "project_id": "preetos-order-agent",
                "private_key_id": "52ef2c399f9d49f7b6af42f061b10706419aeb89",
                "private_key": "",  # Will be set below
                "client_email": "preeetos-sheets-agent@preetos-order-agent.iam.gserviceaccount.com",
                "client_id": "114633176250172838577",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/preeetos-sheets-agent%40preetos-order-agent.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }

            # Try each private key format
            for i, key_attempt in enumerate(private_key_attempts):
                print(f"Trying private key format {i+1}...")
                creds_data["private_key"] = key_attempt
                try:
                    # Test if this format works
                    test_creds = service_account.Credentials.from_service_account_info(
                        creds_data, scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                    print(f"Private key format {i+1} worked!")
                    break
                except Exception as e:
                    print(f"Private key format {i+1} failed: {e}")
                    if i == len(private_key_attempts) - 1:
                        raise ValueError("All private key formats failed. Check your GOOGLE_PRIVATE_KEY environment variable.")

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
