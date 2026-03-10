import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
base_url = os.getenv("BASE_URL")

# NOTE: Since you are on a Twilio Trial account, 
# this MUST be a verified number in your Twilio console!
to_number = "+918439614077"  # <--- Change this to your real phone number

try:
    print(f"[INIT] Initializing Twilio Client...")
    client = Client(account_sid, auth_token)

    print(f"[CALL] Calling: {to_number}")
    print(f"[FROM] From Twilio Number: {twilio_number}")
    print(f"[WEBHOOK] Webhook URL: {base_url}/voice")
    
    # This single line is what tells Twilio to actually dial the phone
    call = client.calls.create(
        to=to_number,
        from_=twilio_number,
        url=f"{base_url}/voice"
    )

    print(f"[SUCCESS] Call successfully triggered!")
    print(f"[ID] Call SID: {call.sid}")
    print("\n[WAIT] Your phone should start ringing in a few seconds... Pick it up to talk to the AI!")

except Exception as e:
    print(f"\n[ERROR] Error triggering call: {e}")
    print("\nDid you remember to:")
    print("1. Update TWILIO_AUTH_TOKEN in the .env file?")
    print("2. Update BASE_URL with your active ngrok URL in the .env file?")
    print("3. Verify your personal phone number on your Twilio Trial account?")
