import os
import requests
from typing import Dict, Optional, List

class HotelAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.assistant_id = None
        self.phone_number_id = "1549a87e-67ef-4c95-b5c6-7fead07d2130"

    def list_phone_numbers(self) -> List[Dict]:
        """List all phone numbers"""
        url = f"{self.base_url}/phone-number"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_assistant(self) -> Dict:
        """Create a new assistant with hotel concierge configuration"""
        url = f"{self.base_url}/assistant"
        
        config = {
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-3",
                "language": "en"
            },
            "model": {
                "provider": "google",
                "model": "gemini-2.0-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are Ellie, a professional concierge at Bella Vista Suites, a luxury boutique hotel located on the shores of Lake Geneva.

Key Responsibilities:
- Handle room bookings and spa appointments
- Provide information about hotel amenities and services
- Give local recommendations
- Process payments and handle deposits

Communication Guidelines:
- Maintain a warm and professional tone
- Ask only ONE question at a time
- Verify all details before proceeding
- Keep conversations natural and flowing
- Never share sensitive guest information

Hotel Details:
- Address: 335 Wrigley Drive, Lake Geneva, WI 53147
- Phone: (262) 248-2100
- 39 Luxury Suites available
- Full-service spa and amenities
- Beachfront location"""
                    }
                ],
                "temperature": 0.7
            },
            "voice": {
                "provider": "playht",
                "voiceId": "jennifer"
            },
            "firstMessage": "Thank you for calling Bella Vista Suites, this is Ellie. How may I assist you today?",
            "firstMessageMode": "assistant-speaks-first",
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": 1800,
            "backgroundSound": "office",
            "name": "BellaVista Hotel Concierge - Ellie",
            "artifactPlan": {
                "recordingEnabled": True,
                "transcriptPlan": {
                    "enabled": True,
                    "assistantName": "Ellie",
                    "userName": "Guest"
                }
            }
        }
        
        response = requests.post(url, headers=self.headers, json=config)
        response.raise_for_status()
        data = response.json()
        self.assistant_id = data["id"]
        return data

    def get_assistant(self, assistant_id: Optional[str] = None) -> Dict:
        """Get assistant details"""
        aid = assistant_id or self.assistant_id
        if not aid:
            raise ValueError("No assistant ID provided")
        
        url = f"{self.base_url}/assistant/{aid}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_phone_number(self) -> Dict:
        """Update phone number configuration to use our assistant"""
        if not self.assistant_id:
            raise ValueError("Create an assistant first")

        # First get the current phone number configuration
        url = f"{self.base_url}/phone-number/{self.phone_number_id}"
        get_response = requests.get(url, headers=self.headers)
        get_response.raise_for_status()
        current_config = get_response.json()

        # Update only the necessary fields
        update_config = {
            "assistantId": self.assistant_id,
            "name": "BellaVista Main Line",
            # Preserve other existing configuration
            "type": current_config.get("type", "phone"),
            "status": current_config.get("status", "active")
        }
        
        # Make the update request
        response = requests.patch(url, headers=self.headers, json=update_config)
        response.raise_for_status()
        return response.json()

    def list_calls(self, limit: int = 10) -> List[Dict]:
        """List recent calls"""
        url = f"{self.base_url}/call"
        params = {"limit": limit}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_call(self, call_id: str) -> Dict:
        """Get details of a specific call"""
        url = f"{self.base_url}/call/{call_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

def main():
    # Initialize with your API key
    api_key = "4aff2cad-02c0-4e1a-8363-99a0391569a0"
    hotel_ai = HotelAI(api_key)

    # List existing phone numbers
    print("Listing existing phone numbers...")
    numbers = hotel_ai.list_phone_numbers()
    print("Available phone numbers:")
    for number in numbers:
        print(f"Number: {number.get('phoneNumber')} - ID: {number.get('id')}")

    # Create the assistant
    print("\nCreating assistant...")
    assistant = hotel_ai.create_assistant()
    print(f"Assistant created with ID: {assistant['id']}")

    # Update phone number to use this assistant
    print("\nUpdating phone number configuration...")
    try:
        phone_config = hotel_ai.update_phone_number()
        print("Phone number updated successfully")
        print(f"Configuration: {phone_config}")
    except Exception as e:
        print(f"Error updating phone number: {str(e)}")
        print("You may need to configure the phone number manually in the Vapi dashboard:")
        print(f"1. Go to the Vapi dashboard")
        print(f"2. Find phone number: +1 (631) 527 0088")
        print(f"3. Set the assistant ID to: {assistant['id']}")

    # List recent calls
    print("\nRecent calls:")
    try:
        calls = hotel_ai.list_calls(limit=5)
        if not calls:
            print("No recent calls found")
        else:
            for call in calls:
                print(f"Call ID: {call.get('id')} - Status: {call.get('status', 'N/A')}")
    except Exception as e:
        print(f"Error listing calls: {str(e)}")

if __name__ == "__main__":
    main() 