import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1gp5SGwhxzq3JstCUsTfB5mE4jB2y1oTwrjJ9yZ7GACg'
TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

class AvailabilityTool:
    def __init__(self):
        self.spreadsheet_id = SPREADSHEET_ID
        self.creds = None
        self.sheet = None
        
    def authenticate(self) -> bool:
        """Handle Google Sheets authentication with improved token persistence"""
        try:
            if os.path.exists(TOKEN_PATH):
                with open(TOKEN_PATH, 'rb') as token:
                    self.creds = pickle.load(token)

            # If there are no (valid) credentials available, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("Refreshing expired credentials...")
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_PATH):
                        raise FileNotFoundError(f"{CREDENTIALS_PATH} not found. Please ensure you've added your Google Cloud credentials file.")
                    
                    print("Initiating new authentication flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                    self.creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(TOKEN_PATH, 'wb') as token:
                    print("Saving credentials for future use...")
                    pickle.dump(self.creds, token)

            self.sheet = build('sheets', 'v4', credentials=self.creds).spreadsheets()
            return True
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse and validate date string"""
        try:
            # Try parsing MM/DD/YYYY format
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            return date_obj.strftime('%-m/%-d/%Y')  # Format to match sheet
        except ValueError:
            try:
                # Try parsing YYYY-MM-DD format
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%-m/%-d/%Y')  # Format to match sheet
            except ValueError:
                return None

    def check_availability(self, date: str, room_type: str = None) -> Dict:
        """Check room availability for a specific date and optional room type"""
        try:
            # Validate and format date
            formatted_date = self.parse_date(date)
            if not formatted_date:
                return {
                    'success': False,
                    'error': 'Invalid date format. Please use MM/DD/YYYY or YYYY-MM-DD',
                    'rooms': []
                }

            range_name = 'Sheet1!A2:H'  # Skip header row
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            if not rows:
                return {
                    'success': True,
                    'rooms': [],
                    'message': 'No rooms found in the system'
                }
            
            available_rooms = []
            for row in rows:
                if len(row) < 4:  # Skip incomplete rows
                    continue
                    
                row_date = row[0]
                row_room_type = row[1]
                rate = row[2]
                availability = row[3]
                size = row[4] if len(row) > 4 else "N/A"
                max_guests = row[5] if len(row) > 5 else "N/A"
                description = row[6] if len(row) > 6 else "N/A"
                amenities = row[7] if len(row) > 7 else "N/A"
                
                if row_date == formatted_date and availability.lower() == 'available':
                    if room_type is None or room_type.lower() in row_room_type.lower():
                        available_rooms.append({
                            'date': row_date,
                            'room_type': row_room_type,
                            'rate': float(rate),
                            'size': size,
                            'max_guests': int(max_guests) if max_guests != "N/A" else "N/A",
                            'description': description,
                            'amenities': amenities
                        })
            
            return {
                'success': True,
                'rooms': available_rooms,
                'message': f"Found {len(available_rooms)} available room(s) for {formatted_date}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error checking availability: {str(e)}",
                'rooms': []
            }

def create_vapi_tool(api_key: str) -> Optional[Dict]:
    """Create the availability checking tool in Vapi"""
    url = "https://api.vapi.ai/tool"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    tool_config = {
        "type": "function",
        "function": {
            "name": "check_room_availability",
            "description": "Check room availability in the hotel's booking system for a specific date and optional room type. Returns available rooms with details including rates, size, max guests, and amenities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date to check availability for (format: MM/DD/YYYY or YYYY-MM-DD)"
                    },
                    "room_type": {
                        "type": "string",
                        "description": "Optional. The specific type of room to check for (e.g., 'King Room', 'Two-Bedroom Suite')"
                    }
                },
                "required": ["date"]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=tool_config)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error creating Vapi tool: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def main():
    # Initialize and authenticate the tool
    tool = AvailabilityTool()
    if not tool.authenticate():
        print("Failed to authenticate with Google Sheets")
        return

    # Test the availability checker with a specific date
    test_date = "3/1/2024"  # Changed to a date we know has available rooms
    result = tool.check_availability(test_date)
    
    if result['success']:
        print(f"\nAvailability check for {test_date}:")
        if result['rooms']:
            for room in result['rooms']:
                print(f"\nRoom Type: {room['room_type']}")
                print(f"Rate: ${room['rate']}")
                print(f"Size: {room['size']} m²")
                print(f"Max Guests: {room['max_guests']}")
                print(f"Amenities: {room['amenities']}")
        else:
            print("No rooms available for this date")
    else:
        print(f"Error: {result['error']}")

    # Create the tool in Vapi
    api_key = os.getenv('VAPI_API_KEY', '4aff2cad-02c0-4e1a-8363-99a0391569a0')
    vapi_tool = create_vapi_tool(api_key)
    
    if vapi_tool:
        print("\nSuccessfully created availability checking tool in Vapi!")
        print(f"Tool ID: {vapi_tool.get('id')}")
    else:
        print("\nFailed to create tool in Vapi")

if __name__ == "__main__":
    main() 