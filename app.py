import os
import requests
from flask import Flask, request, jsonify
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "turisztikaichatbot2026")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "IDE_JÖN_A_META_PAGE_ACCESS_TOKEN")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "IDE_JÖN_AZ_IBM_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "IDE_JÖN_A_PROJECT_ID")

credentials = {
    "url": "https://eu-de.ml.cloud.ibm.com",
    "apikey": WATSONX_API_KEY
}
params = {
    GenParams.MAX_NEW_TOKENS: 200,
    GenParams.TEMPERATURE: 0.7
}
model = Model(
    model_id="meta-llama/llama-3-70b-instruct",
    params=params,
    credentials=credentials,
    project_id=WATSONX_PROJECT_ID
)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook sikeresen ellenőrizve!")
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def handle_messages():
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                message_text = messaging_event.get("message", {}).get("text")

                if sender_id and message_text:
                    # Válasz generálása watsonx.ai-val
                    bot_response = generate_watsonx_response(message_text)
                    # Válasz visszaküldése a Messengernek
                    send_messenger_message(sender_id, bot_response)

    return "EVENT_RECEIVED", 200

def generate_watsonx_response(user_text):
    try:
        prompt = f"Egy segítőkész turisztikai asszisztens vagy. Válaszolj tömören:\nFelhasználó: {user_text}\nAsszisztens:"
        response = model.generate_text(prompt=prompt)
        return response.strip()
    except Exception as e:
        print(f"watsonx hiba: {e}")
        return "Sajnálom, jelenleg nem tudtam feldolgozni a kérést."

def send_messenger_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
