import os
import json
from datetime import datetime
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# --- Data Models ---
class LeadInfo(BaseModel):
    name: str = Field(..., description="Name of the lead")
    company: Optional[str] = Field(None, description="Company name if available")
    service_interest: str = Field(..., description="Service they are interested in (Marketing, AI, Real Estate, etc)")
    budget: Optional[str] = Field(None, description="Budget range")
    timeline: Optional[str] = Field(None, description="Timeline for implementation")
    phone: Optional[str] = Field(None, description="Phone number for follow-up")

# --- Tools ---
def save_lead_to_crm(name: str, service_interest: str, budget: str = "Unknown", phone: str = "Unknown", timeline: str = "Unknown") -> str:
    """
    Saves a qualified lead to the CRM database (simulated JSON file).
    Call this tool ONLY when you have gathered at least the Name and Service Interest.
    """
    lead_data = {
        "id": f"LEAD-{int(datetime.now().timestamp())}",
        "name": name,
        "service_interest": service_interest,
        "budget": budget,
        "phone": phone,
        "timeline": timeline,
        "status": "QUALIFIED_HOT",
        "timestamp": datetime.now().isoformat()
    }
    
    # Simulate DB write
    file_path = "leads_db.json"
    existing_leads = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                existing_leads = json.load(f)
        except:
            pass
    
    existing_leads.append(lead_data)
    
    with open(file_path, "w") as f:
        json.dump(existing_leads, f, indent=2)
        
    return f"SUCCESS: Lead {name} saved to CRM with ID {lead_data['id']}. Schedule a follow-up call."

# --- Agent Definition ---
def create_receptionist_agent():
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        description="You are Sarah, a friendly and professional AI receptionist for 'Skylix Agency'.",
        instructions=[
            "Your goal is to qualify incoming leads for our AI & Marketing services.",
            "Always be polite, professional, and concise.",
            "Ask one question at a time. Do not overwhelm the user.",
            "Required information to gather: Name, Service Interest, Budget, Timeline, Phone Number.",
            "If the user seems hesitant about budget, give them ranges (e.g., <$1k, $1k-$5k, $5k+).",
            "Once you have at least Name and Service Interest (and ideally Phone), call the 'save_lead_to_crm' tool.",
            "After saving the lead, thank them and say a specialist will call them shortly. Then end the conversation."
        ],
        tools=[save_lead_to_crm],
        show_tool_calls=True,
        markdown=True
    )

# --- Interactive CLI ---
def run_receptionist():
    agent = create_receptionist_agent()
    
    print("\n" + "="*50)
    print("📞 INBOUND CALL SIMULATOR - SKYLIX AGENCY")
    print("="*50)
    print("Agent: Hello! Thanks for calling Skylix Agency. I'm Sarah, an AI assistant. How can I help you today?")
    
    # Initial history
    history = []
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Goodbye! Have a great day.")
                break
                
            response = agent.run(user_input)
            print(f"\n🤖 Sarah: {response.content}")
            
            # Check if the tool was called (simulated by checking if conversation implies closure)
            if "specialist will call you" in str(response.content).lower():
                print("\n[System]: Call ended. Lead captured.")
                break
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    run_receptionist()
