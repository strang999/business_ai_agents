import os
import sys
import time
from dotenv import load_dotenv

# Add the current directory to path so we can import from agent.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agent import PropertyFindingAgent
except ImportError:
    # If running from root, adjust import
    sys.path.append(os.path.join(os.getcwd(), 'skylix_portfolio', 'real_estate'))
    from agent import PropertyFindingAgent

# Mock WhatsApp Interface
class WhatsAppSimulator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not self.api_key or not self.firecrawl_key:
            print("⚠️  Error: Missing API keys. Please check your .env file.")
            print("Required: OPENAI_API_KEY, FIRECRAWL_API_KEY")
            sys.exit(1)
            
        self.agent = PropertyFindingAgent(
            firecrawl_api_key=self.firecrawl_key,
            openai_api_key=self.api_key
        )
        self.user_data = {}

    def send_message(self, text):
        print(f"\n🤖 Skylix Agent: {text}")
        time.sleep(0.5)  # Simulate typing delay

    def receive_message(self):
        return input("\n👤 You: ").strip()

    def start_conversation(self):
        print("\n" + "="*40)
        print("📱 SKYLIX REAL ESTATE ASSISTANT")
        print("="*40)

        self.send_message("Hello! 👋 I'm Sarah, your Skylix Real Estate Assistant.")
        self.send_message("I can help you find your dream property in seconds.")
        self.send_message("To get started, which city are you looking to buy in? (e.g., Bangalore, Mumbai)")

        city = self.receive_message()
        self.user_data['city'] = city

        self.send_message(f"Great choice! {city} is a vibrant market.")
        self.send_message("Are you looking for a 'Flat' or an 'Individual House'?")

        prop_type = self.receive_message()
        self.user_data['type'] = prop_type if 'house' not in prop_type.lower() else 'Individual House'
        if 'flat' not in self.user_data['type'].lower() and 'house' not in self.user_data['type'].lower():
             self.user_data['type'] = 'Flat' # Default

        self.send_message("Understood. And what is your maximum budget in Crores? (e.g., 1.5, 5)")

        try:
            budget = float(self.receive_message())
        except ValueError:
            budget = 2.0 # Default
            self.send_message("I didn't catch that number, so I'll assume around 2.0 Cr for now.")
        
        self.user_data['budget'] = budget

        self.send_message("Perfect! 🔍 I'm checking our latest listings for you now...")
        self.send_message("This usually takes about 10-20 seconds as I scan multiple portals...")

        # Call the actual agent
        try:
            results = self.agent.find_properties(
                city=self.user_data['city'],
                max_price=self.user_data['budget'],
                property_type=self.user_data['type']
            )
            
            self.send_message("Here is what I found for you! 👇")
            print("\n" + "-"*40)
            print(results)
            print("-" * 40)
            
            self.send_message("Would you like to schedule a site visit for any of these? (yes/no)")
            response = self.receive_message()
            
            if 'yes' in response.lower():
                self.send_message("Great! 📅 I've marked this as a hot lead. Our human agent will call you within 10 minutes to confirm the time.")
            else:
                self.send_message("No problem! I'll keep looking for better matches and WhatsApp you if something comes up. 👋")

        except Exception as e:
            self.send_message(f"Oops! I encountered a glitch: {str(e)}")

if __name__ == "__main__":
    bot = WhatsAppSimulator()
    bot.start_conversation()
