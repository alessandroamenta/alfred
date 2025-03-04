import os
import requests
from typing import Dict, List
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
VAPI_API_KEY = os.getenv('VAPI_API_KEY')
ASSISTANT_ID = '3113a0ea-18f7-4898-b936-36010399eb93'  # Correct assistant ID
AVAILABILITY_TOOL_ID = '93521a4e-dc20-4bf6-bd49-12c4300afd13'  # Latest tool ID from availability_tool.py

class KnowledgeBaseManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_knowledge_base(self) -> Dict:
        """Create a knowledge base with hotel website content"""
        url = f"{self.base_url}/knowledge-base"
        
        config = {
            "provider": "trieve",
            "name": "Bella Vista Hotel Knowledge Base",
            "vectorStoreProviderId": "bella_vista_kb",
            "searchPlan": {
                "searchType": "hybrid",
                "topK": 5,
                "removeStopWords": True,
                "scoreThreshold": 0.7
            }
        }
        
        print("Creating knowledge base with config:", json.dumps(config, indent=2))
        response = requests.post(url, headers=self.headers, json=config)
        
        if response.status_code != 200 and response.status_code != 201:
            print(f"Error response: {response.text}")
            response.raise_for_status()
            
        return response.json()
    
    def update_assistant(self, assistant_id: str, knowledge_base_id: str) -> Dict:
        """Update the assistant to use the knowledge base"""
        url = f"{self.base_url}/assistant/{assistant_id}"
        
        update_config = {
            "model": {
                "knowledgeBaseId": knowledge_base_id,
                "provider": "google",
                "model": "gemini-2.0-flash",
                "voice": {
                    "provider": "deepgram",
                    "voiceId": "luna"
                },
                "messages": [
                    {
                        "role": "system",
                        "content": """You are Alfred, the AI concierge for Bella Vista Suites, a luxury hotel on Lake Geneva.
                        You help guests with room availability, bookings, and general inquiries.
                        You have access to real-time room availability through the hotel's booking system.
                        Be professional, courteous, and helpful at all times."""
                    }
                ],
                "temperature": 0.7
            }
        }
        
        response = requests.patch(url, headers=self.headers, json=update_config)
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        response.raise_for_status()
        return response.json()

def update_assistant():
    """Update the assistant configuration with voice settings"""
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    config = {
        "voice": {
            "provider": "deepgram",
            "voiceId": "luna"
        },
        "model": {
            "provider": "anthropic",
            "model": "claude-3-opus-20240229"
        }
    }
    
    try:
        print("Updating assistant configuration...")
        response = requests.patch(url, headers=headers, json=config)
        response.raise_for_status()
        print("Successfully updated assistant configuration!")
        return response.json()
    except Exception as e:
        print(f"Error updating assistant: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def main():
    # Initialize with your API key
    api_key = "4aff2cad-02c0-4e1a-8363-99a0391569a0"
    kb_manager = KnowledgeBaseManager(api_key)
    
    try:
        # Create knowledge base with hotel information
        print("Creating knowledge base...")
        kb = kb_manager.create_knowledge_base()
        print(f"Knowledge base created with ID: {kb['id']}")
        
        # Update the existing assistant to use the knowledge base
        assistant_id = "3113a0ea-18f7-4898-b936-36010399eb93"  # Your existing assistant ID
        print("\nUpdating assistant with knowledge base...")
        updated_assistant = kb_manager.update_assistant(assistant_id, kb['id'])
        print("Assistant updated successfully!")
        print(f"Assistant config: {updated_assistant}")
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response details: {e.response.text}")

if __name__ == "__main__":
    update_assistant() 