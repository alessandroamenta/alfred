import os
import requests
from typing import Dict, List
import json

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
- Beachfront location with walking distance to downtown

Room Types:
1. Presidential Suite (1,170 sq ft) - Two bedrooms, lake view
2. Governor Suite (1,120 sq ft) - Two bedrooms, lake view
3. Penthouse Suite (1,720 sq ft) - Two bedrooms, double balcony
4. Woodland Suite (560 sq ft) - Park view
5. Lakeside Suite (550 sq ft) - Lake view
6. Beachview Suite (700 sq ft) - Lake view, double Jacuzzi
7. Villa Suite (600 sq ft) - Lake view
8. Parkview Suite (475 sq ft) - Park view
9. St. Moritz Suite (750 sq ft) - Partial lake view

All suites include:
- King-sized pillow-top beds
- Private balcony
- Jetted bathtub
- Rain-head shower
- Kitchenette/wet bar
- Sofa bed
- Flat-screen TVs
- Free WiFi"""
                    }
                ]
            }
        }
        
        response = requests.patch(url, headers=self.headers, json=update_config)
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        response.raise_for_status()
        return response.json()

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
    main() 