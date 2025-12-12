import os
import json
import sys
import time
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Import existing functionality
try:
    from agent import PropertyFindingAgent, PropertyData
except ImportError:
    # Handle import if running from different directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from agent import PropertyFindingAgent, PropertyData

# Load environment variables
load_dotenv()

# --- Configuration & Company Details ---
COMPANY_DETAILS = {
    "name": "Skylix Real Estate",
    "address": "123 Tech Park, Bangalore, KA",
    "phone": "+91-9876543210",
    "website": "www.skylix-realestate.com",
    "specialties": ["Luxury Apartments", "Commercial Spaces", "Investment Advisory"],
    "operating_hours": "Mon-Sat, 9 AM - 7 PM"
}

# --- Database / Memory System ---
class LeadDatabase:
    """Simple JSON-based database for storing leads and user history"""
    def __init__(self, db_file="real_estate_leads.json"):
        self.db_file = db_file
        self.ensure_db()

    def ensure_db(self):
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({"leads": {}, "conversations": {}}, f)

    def _read_db(self):
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except Exception:
            return {"leads": {}, "conversations": {}}

    def _write_db(self, data):
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=2)

    def update_lead(self, user_id: str, data: Dict):
        db = self._read_db()
        if user_id not in db["leads"]:
            db["leads"][user_id] = {
                "first_seen": datetime.now().isoformat(),
                "phone": user_id,
                "preferences": {}
            }
        
        # specific updates
        if "preferences" in data:
            db["leads"][user_id]["preferences"].update(data["preferences"])
        else:
            db["leads"][user_id].update(data)
            
        db["leads"][user_id]["last_active"] = datetime.now().isoformat()
        self._write_db(db)
        print(f"💾 [DB] Updated lead data for {user_id}")

    def save_message(self, user_id: str, sender: str, text: str):
        """Log message for history"""
        db = self._read_db()
        if user_id not in db["conversations"]:
            db["conversations"][user_id] = []
        
        db["conversations"][user_id].append({
            "timestamp": datetime.now().isoformat(),
            "sender": sender, # 'user' or 'bot'
            "text": text
        })
        self._write_db(db)

    def get_user_context(self, user_id: str) -> Dict:
        db = self._read_db()
        return db["leads"].get(user_id, {})

# --- Main WhatsApp Bot Logic ---
class RealEstateWhatsAppBot:
    def __init__(self):
        self.db = LeadDatabase()
        
        # Initialize the property search agent
        # We assume keys are in .env or we prompt for them
        api_key = os.getenv("OPENAI_API_KEY")
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not api_key or not firecrawl_key:
            print("⚠️ API Keys missing (OPENAI_API_KEY or FIRECRAWL_API_KEY). Search functionality might fail.")
        
        self.property_agent = PropertyFindingAgent(
            firecrawl_api_key=firecrawl_key or "sk-dummy", # Fallback for init, will fail on call if invalid
            openai_api_key=api_key or "sk-dummy"
        )
        
        # Session state to track user flow (e.g., are we waiting for a budget?)
        # In a production app, this should be in Redis or DB
        self.session_state = {} 

    def handle_incoming_message(self, user_id: str, message: str) -> str:
        """
        Main router for incoming messages. 
        Returns the text response to send back to WhatsApp.
        """
        # 1. Log incoming
        self.db.save_message(user_id, "user", message)
        
        # 2. Get Context
        context = self.db.get_user_context(user_id)
        state = self.session_state.get(user_id, {"step": "home"})
        
        response = ""
        
        # 3. Simple Workflow Logic (State Machine)
        message_lower = message.lower()
        
        # Global Commands
        if message_lower in ["hi", "hello", "start", "menu"]:
            self.session_state[user_id] = {"step": "home"}
            response = (
                f"Welcome to {COMPANY_DETAILS['name']}! 🏠\n"
                f"I'm your AI Real Estate Assistant.\n\n"
                "I can help you with:\n"
                "1. 🔍 Finding a property\n"
                "2. 📞 Contacting an agent\n"
                "3. 🏢 Company details\n\n"
                "What would you like to do? (Type 1, 2, or 3)"
            )
            
        elif state["step"] == "home":
            if "1" in message or "find" in message_lower:
                self.session_state[user_id] = {"step": "collect_city"}
                response = "Great! 🌍 Which city should we search in? (e.g., Bangalore, Mumbai)"
            elif "2" in message or "contact" in message_lower:
                response = (
                    f"Let's get you connected! 📞\n"
                    f"You can call us directly at {COMPANY_DETAILS['phone']}\n"
                    "Or typically our agents will call you back if you share your requirements."
                )
            elif "3" in message or "company" in message_lower:
                response = (
                    f"ℹ️ *About {COMPANY_DETAILS['name']}*\n"
                    f"📍 Address: {COMPANY_DETAILS['address']}\n"
                    f"🌐 Website: {COMPANY_DETAILS['website']}\n"
                    f"🕒 Hours: {COMPANY_DETAILS['operating_hours']}\n"
                    "We specialize in: " + ", ".join(COMPANY_DETAILS['specialties'])
                )
            else:
                response = "I didn't quite catch that. Please type 1, 2, or 3. 🤔"

        # --- Property Search Flow ---
        elif state["step"] == "collect_city":
            self.db.update_lead(user_id, {"preferences": {"city": message}})
            self.session_state[user_id] = {"step": "collect_budget"}
            response = f"Got it, {message}. 💸 What is your maximum budget in Crores? (e.g., 2.5)"
            
        elif state["step"] == "collect_budget":
            try:
                # Simple extraction, in real world might use LLM to extract number
                import re
                budget_match = re.search(r"(\d+(\.\d+)?)", message)
                if budget_match:
                    budget = float(budget_match.group(1))
                    self.db.update_lead(user_id, {"preferences": {"budget": budget}})
                    self.session_state[user_id] = {"step": "collect_type"}
                    response = "Noted. 🏡 Are you looking for a 'Flat' or 'Individual House'?"
                else:
                    response = "Could not verify the amount. Please just type the number (e.g. 5.0)"
            except Exception:
                response = "Please enter a valid number (e.g., 2.5)"

        elif state["step"] == "collect_type":
            prop_type = "Flat"
            if "house" in message_lower or "villa" in message_lower:
                prop_type = "Individual House"
            
            self.db.update_lead(user_id, {"preferences": {"type": prop_type}})
            self.session_state[user_id] = {"step": "searching"}  # prevent loops
            
            # --- TRIGGER AI AGENT ---
            response = "Thank you! 🤖 I'm now searching the entire web for real-time listings matching your criteria. This takes about 15 seconds..."
            
            # We return this immediately to the user, but we'd typically trigger a background job.
            # For this synchronous CLI demo, we will just call it next.
            # In a real webhook, we would return 200 OK here and send a follow-up message via API.
            
            return response, True # Signal to run search
            
        else:
            # Fallback Chat using LLM if needed (not implemented here to keep it deterministic)
            response = "I can help you find properties! Type 'start' to begin."

        # 4. Log Response
        self.db.save_message(user_id, "bot", response)
        return response, False

    def perform_search(self, user_id):
        """Execute the heavy AI search task"""
        user_data = self.db.get_user_context(user_id)
        prefs = user_data.get("preferences", {})
        
        print(f"🕵️ SERVER ENGINE: Starting search for {user_id} with {prefs}")
        
        try:
            results = self.property_agent.find_properties(
                city=prefs.get("city", "Bangalore"),
                max_price=prefs.get("budget", 2.0),
                property_type=prefs.get("type", "Flat")
            )
            
            # Save results to memory/DB if needed
            self.db.save_message(user_id, "bot", f"[Search Results]: {results[:50]}...")
            return f"Here is what I found! 🎉\n\n{results}\n\nWould you like to speak to a human agent now to book a visit?"
            
        except Exception as e:
            return f"⚠️ I encountered an error while searching real-time listings: {str(e)}"

# --- Simulation Interface (CLI) ---
def run_cli_simulation():
    bot = RealEstateWhatsAppBot()
    
    print("\n" + "="*50)
    print("📱 WHATSAPP SIMULATOR (Debug Mode)")
    print("="*50)
    
    # Simulate a phone number user ID
    user_id = "+919999988888"
    print(f"Simulating connection from {user_id}")
    
    while True:
        try:
            msg = input(f"\n[{user_id}]: ").strip()
            if msg.lower() in ["exit", "quit"]:
                break
            
            # 1. Get immediate response
            reply, trigger_search = bot.handle_incoming_message(user_id, msg)
            print(f"\n[Bot]: {reply}")
            
            # 2. If 'trigger_search' is True, simulate the async follow-up
            if trigger_search:
                print("\n... (Simulating background processing) ...")
                search_results = bot.perform_search(user_id)
                print(f"\n[Bot - Follow Up]: {search_results}")
                # Reset state after search
                bot.session_state[user_id] = {"step": "home"} 
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_cli_simulation()
