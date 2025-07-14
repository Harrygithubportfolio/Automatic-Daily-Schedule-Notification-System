#!/usr/bin/env python3
"""
Google Calendar OAuth Credentials Generator
Run this script to generate Lambda-compatible credentials for Google Calendar API

Prerequisites:
1. Enable Google Calendar API in Google Cloud Console
2. Create OAuth 2.0 Desktop Application credentials
3. Download credentials.json file to this directory
4. Install required packages: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import json
import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Required scopes for calendar access and webhook setup
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events.readonly'
]

def find_credentials_file():
    """Find OAuth credentials file in current directory"""
    possible_files = ['credentials.json']
    
    # Look for downloaded OAuth files
    for filename in os.listdir('.'):
        if filename.startswith('client_secret_') and filename.endswith('.json'):
            possible_files.append(filename)
    
    for filename in possible_files:
        if os.path.exists(filename):
            return filename
    
    return None

def main():
    print("🔐 GOOGLE CALENDAR OAUTH CREDENTIALS GENERATOR")
    print("=" * 55)
    print("This script generates Lambda-compatible credentials for Google Calendar API")
    print()
    
    # Check for credentials file
    creds_file = find_credentials_file()
    
    if not creds_file:
        print("❌ No OAuth credentials file found!")
        print()
        print("📋 SETUP REQUIRED:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select project")
        print("3. Enable Google Calendar API")
        print("4. Create OAuth consent screen (External)")
        print("5. Add your email as test user")
        print("6. Create OAuth client ID (Desktop application)")
        print("7. Download JSON file to this directory")
        print("8. Run this script again")
        return False
    
    print(f"✅ Found credentials file: {creds_file}")
    
    try:
        print()
        print("🔐 Starting OAuth authentication...")
        print("A browser window will open - please authorize the application")
        print()
        
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        creds = flow.run_local_server(port=0)
        
        print("✅ Authentication successful!")
        
        # Test the API
        print()
        print("🧪 Testing Google Calendar API access...")
        service = build('calendar', 'v3', credentials=creds)
        
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        print(f"✅ Successfully accessed {len(calendars)} calendars:")
        for cal in calendars[:3]:
            print(f"   - {cal.get('summary', 'Unknown Calendar')}")
        
        if len(calendars) > 3:
            print(f"   ... and {len(calendars) - 3} more")
        
        # Test webhook permissions
        print()
        print("🔗 Testing webhook permissions...")
        try:
            # This will fail (expected) but confirms we have the right permissions
            test_watch = {
                'id': 'test-webhook-capability',
                'type': 'web_hook',
                'address': 'https://example.com/webhook'
            }
            
            service.events().watch(calendarId='primary', body=test_watch).execute()
            
        except Exception as e:
            if 'Invalid webhook URL' in str(e) or 'Webhook verification failed' in str(e):
                print("✅ Webhook permissions confirmed")
            else:
                print(f"⚠️ Webhook test result: {e}")
        
        # Create Lambda-compatible credentials
        print()
        print("🔧 Generating Lambda credentials...")
        
        creds_dict = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        
        # Encode for Lambda environment variable
        creds_json = json.dumps(creds_dict)
        encoded_creds = base64.b64encode(creds_json.encode()).decode()
        
        # Save to file
        with open('lambda_credentials.txt', 'w') as f:
            f.write("GOOGLE_CALENDAR_CREDENTIALS=")
            f.write(encoded_creds)
        
        print("🎉 SUCCESS! LAMBDA CREDENTIALS GENERATED")
        print("=" * 50)
        print()
        print("📋 NEXT STEPS:")
        print("1. Copy the credentials below")
        print("2. Go to your Lambda function in AWS Console")
        print("3. Configuration → Environment variables")
        print("4. Add/update: GOOGLE_CALENDAR_CREDENTIALS")
        print("5. Paste the value below")
        print()
        print("🔑 GOOGLE_CALENDAR_CREDENTIALS:")
        print("-" * 50)
        print(encoded_creds)
        print("-" * 50)
        print()
        print(f"💾 Credentials also saved to: lambda_credentials.txt")
        print()
        print("✅ Ready for AWS Lambda deployment!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("- Make sure you've enabled Google Calendar API")
        print("- Check OAuth consent screen is configured")
        print("- Verify you're using Desktop application credentials")
        print("- Try downloading credentials file again")
        
        return False

if __name__ == '__main__':
    success = main()
    
    if success:
        print()
        print("🎉 Setup complete! Continue with AWS Lambda configuration.")
    else:
        print()
        print("❌ Setup failed. Please resolve the issues above and try again.")