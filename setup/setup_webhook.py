#!/usr/bin/env python3
"""
Google Calendar Webhook Setup Script
Run this script to connect Google Calendar webhooks to your AWS Lambda function

Prerequisites:
1. Lambda function deployed with Function URL enabled
2. Google Calendar credentials generated (run generate_google_credentials.py first)
3. lambda_credentials.txt file in current directory
"""

import json
import base64
import os
import requests
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_lambda_function_url():
    """Get Lambda Function URL from user input"""
    print("📋 LAMBDA FUNCTION URL REQUIRED")
    print("-" * 40)
    print("You need your Lambda Function URL from AWS Console:")
    print("1. Go to your Lambda function")
    print("2. Configuration → Function URL")
    print("3. Copy the Function URL")
    print()
    
    while True:
        webhook_url = input("Enter your Lambda Function URL: ").strip()
        
        if not webhook_url:
            print("❌ URL cannot be empty")
            continue
            
        if not webhook_url.startswith('https://'):
            print("❌ URL must start with https://")
            continue
            
        if '.lambda-url.' not in webhook_url:
            print("❌ This doesn't look like a Lambda Function URL")
            continue
            
        return webhook_url

def test_webhook_endpoint(webhook_url):
    """Test if the webhook endpoint is accessible"""
    print(f"🧪 Testing webhook endpoint accessibility...")
    
    try:
        test_payload = {
            "test": "webhook_connectivity",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=test_payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is accessible!")
            return True
        else:
            print(f"⚠️ Webhook endpoint returned status: {response.status_code}")
            print("This might still work - Google's webhook verification is different")
            return True
            
    except Exception as e:
        print(f"❌ Cannot reach webhook endpoint: {e}")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("- Verify the Lambda Function URL is correct")
        print("- Check that Auth type is set to NONE")
        print("- Ensure CORS is enabled")
        return False

def load_google_credentials():
    """Load Google Calendar credentials from file"""
    creds_file = 'lambda_credentials.txt'
    
    if not os.path.exists(creds_file):
        print("❌ lambda_credentials.txt not found!")
        print()
        print("📋 REQUIRED:")
        print("1. Run generate_google_credentials.py first")
        print("2. This will create lambda_credentials.txt")
        print("3. Then run this script again")
        return None
    
    try:
        with open(creds_file, 'r') as f:
            creds_line = f.read().strip()
            encoded_creds = creds_line.replace('GOOGLE_CALENDAR_CREDENTIALS=', '')
        
        # Decode credentials
        creds_json = base64.b64decode(encoded_creds).decode('utf-8')
        creds_dict = json.loads(creds_json)
        
        creds = Credentials.from_authorized_user_info(creds_dict, 
            ['https://www.googleapis.com/auth/calendar.readonly',
             'https://www.googleapis.com/auth/calendar.events.readonly'])
        
        # Refresh if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("❌ Invalid credentials - please regenerate")
                return None
        
        return creds
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def create_webhook(webhook_url, creds):
    """Create Google Calendar webhook"""
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Create unique channel ID
        channel_id = f"lambda-webhook-{int(datetime.now().timestamp())}"
        
        # Set expiration (6 days from now - Google's max for Calendar API)
        expiration_time = datetime.now() + timedelta(days=6)
        expiration_ms = int(expiration_time.timestamp() * 1000)
        
        print(f"🔗 Creating webhook channel...")
        print(f"   Channel ID: {channel_id}")
        print(f"   Webhook URL: {webhook_url}")
        print(f"   Expires: {expiration_time}")
        
        # Create the webhook
        watch_request = {
            'id': channel_id,
            'type': 'web_hook',
            'address': webhook_url,
            'expiration': expiration_ms
        }
        
        watch_response = service.events().watch(
            calendarId='primary',
            body=watch_request
        ).execute()
        
        # Save webhook info for reference
        webhook_info = {
            'channel_id': watch_response.get('id'),
            'resource_id': watch_response.get('resourceId'),
            'webhook_url': webhook_url,
            'created': datetime.now().isoformat(),
            'expires': expiration_time.isoformat()
        }
        
        with open('webhook_info.json', 'w') as f:
            json.dump(webhook_info, f, indent=2)
        
        print()
        print("🎉 WEBHOOK SETUP SUCCESSFUL!")
        print("=" * 40)
        print(f"✅ Channel ID: {webhook_response.get('id')}")
        print(f"✅ Resource ID: {webhook_response.get('resourceId')}")
        print(f"✅ Expires: {expiration_time}")
        print()
        print("💾 Webhook info saved to: webhook_info.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating webhook: {e}")
        
        if 'Webhook verification failed' in str(e):
            print()
            print("🔧 WEBHOOK VERIFICATION FAILED:")
            print("- Make sure your Lambda Function URL is publicly accessible")
            print("- Verify Auth type is set to NONE")
            print("- Check that CORS is properly configured")
            print("- Ensure your Lambda function is deployed and working")
        elif 'Invalid webhook URL' in str(e):
            print()
            print("🔧 INVALID WEBHOOK URL:")
            print("- URL must be HTTPS")
            print("- URL must be publicly accessible")
            print("- Check your Lambda Function URL is correct")
        else:
            print()
            print("🔧 TROUBLESHOOTING:")
            print("- Verify Google Calendar API is enabled")
            print("- Check OAuth credentials are valid")
            print("- Ensure webhook URL is accessible")
        
        return False

def main():
    print("🔗 GOOGLE CALENDAR WEBHOOK SETUP")
    print("=" * 40)
    print("This script connects Google Calendar to your AWS Lambda function")
    print("for real-time notifications when your calendar changes.")
    print()
    
    # Get Lambda Function URL
    webhook_url = get_lambda_function_url()
    print(f"✅ Using webhook URL: {webhook_url}")
    
    # Test endpoint accessibility
    if not test_webhook_endpoint(webhook_url):
        print()
        print("❌ Webhook endpoint test failed. Please fix the issues above.")
        return False
    
    print()
    
    # Load Google credentials
    print("🔐 Loading Google Calendar credentials...")
    creds = load_google_credentials()
    
    if not creds:
        return False
    
    print("✅ Google Calendar credentials loaded successfully")
    
    # Create webhook
    print()
    success = create_webhook(webhook_url, creds)
    
    if success:
        print()
        print("🧪 TESTING INSTRUCTIONS:")
        print("-" * 30)
        print("1. Open your Apple Calendar app")
        print("2. Create/edit/delete an event")
        print("3. Wait 30 seconds for sync")
        print("4. Check your Lambda CloudWatch logs")
        print("5. Look for: '📞 Calendar webhook received'")
        print("6. You should get notification: 'Calendar Updated'")
        print()
        print("⚠️ IMPORTANT NOTES:")
        print("- Webhook expires in 6 days")
        print("- Your Lambda function will auto-renew it")
        print("- Manual renewal: re-run this script if needed")
        print()
        print("🎉 Setup complete! Your calendar is now connected to Lambda.")
        
    return success

if __name__ == '__main__':
    success = main()
    
    if success:
        print()
        print("✅ Webhook setup successful! Your system is now fully automated.")
    else:
        print()
        print("❌ Webhook setup failed. Please resolve the issues above.")