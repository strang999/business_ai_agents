from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
import os
import sys

# Add directory to sys path to import local modules if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from whatsapp_agent import RealEstateWhatsAppBot
from meta_utils import send_whatsapp_message, VERIFY_TOKEN

app = FastAPI(title="Skylix Real Estate WhatsApp Bot")

# Initialize Bot Logic
bot = RealEstateWhatsAppBot()

@app.get("/")
def home():
    return {"status": "ok", "message": "Skylix WhatsApp Webhook is running 🚀"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification for Meta.
    """
    params = request.query_params
    hub_mode = params.get("hub.mode")
    hub_challenge = params.get("hub.challenge")
    hub_verify_token = params.get("hub.verify_token")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook Verified!")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    
    raise HTTPException(status_code=403, detail="Verification failed")

async def process_search_task(user_id: str):
    """
    Background task to perform the search and send the result back.
    """
    print(f"⏳ Background Task: Searching for {user_id}...")
    
    # Run the heavy agent search
    search_result_text = bot.perform_search(user_id)
    
    # Send the result back to the user
    send_whatsapp_message(user_id, search_result_text)
    
    # Reset state
    bot.session_state[user_id] = {"step": "home"}
    print(f"✅ Search completed and sent to {user_id}")

@app.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming WhatsApp messages.
    """
    try:
        data = await request.json()
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        # Check if it's a message
        if "messages" in value:
            message_data = value["messages"][0]
            from_number = message_data["from"]  # The user's phone number
            msg_body = ""

            # Extract text
            if message_data["type"] == "text":
                msg_body = message_data["text"]["body"]
            else:
                msg_body = "[Media/Other]"
            
            print(f"📩 Received from {from_number}: {msg_body}")
            
            # 1. Process Message with Bot Logic
            reply_text, trigger_search = bot.handle_incoming_message(from_number, msg_body)
            
            # 2. Send Immediate Reply
            send_whatsapp_message(from_number, reply_text)
            
            # 3. Trigger Search if needed
            if trigger_search:
                background_tasks.add_task(process_search_task, from_number)
                
        return {"status": "received"}
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        # Return 200 to prevent Meta from retrying endlessly on bad logic
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Server on Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
