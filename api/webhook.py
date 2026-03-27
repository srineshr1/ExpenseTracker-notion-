import os
import json
import requests
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Load secrets from Vercel Environment Variables
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET") # A secret password you invent
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")

groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/api/webhook', methods=['POST'])
def handle_sms():
    # 1. Security Check: Make sure the request is from your phone
    provided_secret = request.headers.get("Authorization")
    if provided_secret != f"Bearer {WEBHOOK_SECRET}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    sms_text = data.get("text", "")
    
    if not sms_text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # 2. Ask Groq API to parse the UPI SMS
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial parser for Indian UPI SMS messages. Extract the amount (number), party name (string), category (string), and type (must be exactly 'Expense' or 'Income'). If the SMS says 'debited', 'paid', or 'sent', it is an Expense. If it says 'credited', 'received', or 'added', it is an Income. Respond ONLY in valid JSON format like: {\"amount\": 150, \"party\": \"Swiggy\", \"category\": \"Food\", \"type\": \"Expense\"}."
                },
                {
                    "role": "user",
                    "content": sms_text
                }
            ],
            model="llama3-8b-8192",
            temperature=0,
            response_format={"type": "json_object"} # Groq supports strict JSON!
        )
        
        parsed_data = json.loads(chat_completion.choices[0].message.content)

        # 3. Send parsed data to Notion
        notion_url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Matches your new Notion table structure: Amount, Party, Type, Category
        notion_data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Amount": {"number": parsed_data.get("amount", 0)},
                "Party": {"title": [{"text": {"content": parsed_data.get("party", "Unknown")}}]},
                "Type": {"select": {"name": parsed_data.get("type", "Expense")}},
                "Category": {"select": {"name": parsed_data.get("category", "Uncategorized")}}
            }
        }
        
        notion_res = requests.post(notion_url, headers=headers, json=notion_data)
        notion_res.raise_for_status() # Will raise an error if Notion fails

        return jsonify({"status": "success", "parsed": parsed_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500