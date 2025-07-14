import json
import os
import boto3
from datetime import datetime, timedelta
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    try:
        # Initialize the notifier
        notifier = LambdaScheduleNotifier()
        
        # Get today's events and send notifications
        result = notifier.run()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Schedule notifications sent successfully',
                'events_count': result.get('events_count', 0),
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

class LambdaScheduleNotifier:
    def __init__(self):
        self.today = datetime.now()
        
    def get_google_calendar_service(self):
        """
        Get Google Calendar service using credentials from environment variables
        """
        creds = None
        
        # Get credentials from environment variable (base64 encoded)
        creds_data = os.environ.get('GOOGLE_CALENDAR_CREDENTIALS')
        if creds_data:
            try:
                # Decode base64 credentials
                creds_json = base64.b64decode(creds_data).decode('utf-8')
                creds_dict = json.loads(creds_json)
                
                creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
                
                # If there are no (valid) credentials available, return None
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        print("Invalid credentials")
                        return None
                        
            except Exception as e:
                print(f"Error processing credentials: {e}")
                return None
        else:
            print("No Google Calendar credentials found in environment")
            return None
        
        service = build('calendar', 'v3', credentials=creds)
        return service
    
    def get_calendar_events(self):
        """
        Get today's events from Google Calendar
        """
        try:
            service = self.get_google_calendar_service()
            if not service:
                return []
            
            # Get start and end of today
            today_start = self.today.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            # Convert to RFC3339 format
            time_min = today_start.isoformat() + 'Z'
            time_max = today_end.isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Parse the datetime
                if 'T' in start:
                    event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = event_time.strftime('%H:%M')
                else:
                    time_str = 'All day'
                
                formatted_events.append({
                    'time': time_str,
                    'title': event.get('summary', 'No title'),
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"Error getting calendar events: {e}")
            return []
    
    def send_pushover_notification(self, title, message):
        """
        Send notification using Pushover
        """
        try:
            # Get Pushover credentials from environment variables
            token = os.environ.get('PUSHOVER_TOKEN')
            user = os.environ.get('PUSHOVER_USER')
            
            if not token or not user:
                print("Pushover credentials not found in environment variables")
                return False
            
            url = "https://api.pushover.net/1/messages.json"
            data = {
                "token": token,
                "user": user,
                "title": title,
                "message": message,
                "priority": 0,
                "sound": "default"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                print("Pushover notification sent successfully")
                return True
            else:
                print(f"Error sending Pushover notification: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending Pushover notification: {e}")
            return False
    
    def format_schedule_message(self, events):
        """
        Format events into a readable message
        """
        if not events:
            return "No events scheduled for today! 🎉"
        
        message = f"Today's Schedule ({len(events)} events):\n\n"
        
        for event in events:
            location_text = f" ({event['location']})" if event['location'] else ""
            message += f"• {event['time']} - {event['title']}{location_text}\n"
        
        return message
    
    def run(self):
        """
        Main function to get events and send notifications
        """
        print("Fetching today's calendar events from Google Calendar...")
        events = self.get_calendar_events()
        
        title = f"Daily Schedule - {self.today.strftime('%A, %B %d')}"
        message = self.format_schedule_message(events)
        
        print(f"\n{title}")
        print(f"{message}")
        
        # Send notification
        success = self.send_pushover_notification(title, message)
        
        return {
            'events_count': len(events),
            'notification_sent': success,
            'events': events
        }

# For local testing
if __name__ == "__main__":
    # Test the function locally
    test_event = {}
    test_context = {}
    
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))