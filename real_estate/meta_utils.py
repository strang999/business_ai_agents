import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Meta API Configuration
WHATSAPP_VERSION = "v17.0"
PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")

def send_whatsapp_message(to_number: str, text: str):
    """
    Sends a text message to a WhatsApp user using the Meta Cloud API.
    """
    if not (PHONE_NUMBER_ID and ACCESS_TOKEN):
        print("⚠️ Meta API Credentials missing. Message not sent:", text)
        return False
        
    url = f"https://graph.facebook.com/{WHATSAPP_VERSION}/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending WhatsApp message: {e}")
        if response:
            print("Response:", response.text)
        return False
